import re

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import ChatRecord, KnowledgeDoc
from app.services.category_service import detect_category_by_question
from app.services.safety_service import (
    build_safety_warning,
    detect_sensitive_info,
    mask_sensitive_info,
)
from app.services import llm_service, vector_service


QUESTION_KEYWORDS = [
    "社保",
    "养老",
    "失业",
    "工伤",
    "医保",
    "医疗",
    "医院",
    "报销",
    "学校",
    "入学",
    "教育",
    "学生",
    "就业",
    "创业",
    "补贴",
    "招聘",
    "住房",
    "公积金",
    "租房",
    "买房",
    "公交",
    "地铁",
    "驾驶证",
    "交通",
    "投诉",
    "占道",
    "噪声",
    "城管",
    "办理",
    "材料",
    "流程",
    "条件",
]


def extract_search_terms(question: str) -> list[str]:
    terms = [keyword for keyword in QUESTION_KEYWORDS if keyword in question]
    terms.extend(term for term in re.split(r"\W+", question) if len(term) >= 2)

    unique_terms: list[str] = []
    for term in terms:
        if term and term not in unique_terms:
            unique_terms.append(term)
    return unique_terms[:8]


def _build_keyword_filter(terms: list[str]):
    filters = []
    for term in terms:
        like_term = f"%{term}%"
        filters.append(KnowledgeDoc.title.like(like_term))
        filters.append(KnowledgeDoc.content.like(like_term))
    return or_(*filters)


def _query_related_docs(
    question: str,
    category_id: int | None,
    db: Session,
) -> list[KnowledgeDoc]:
    terms = extract_search_terms(question)
    if not terms:
        return []

    base_query = db.query(KnowledgeDoc).filter(
        KnowledgeDoc.status == "active",
        _build_keyword_filter(terms),
    )

    if category_id is not None:
        preferred_docs = (
            base_query.filter(KnowledgeDoc.category_id == category_id)
            .order_by(KnowledgeDoc.updated_at.desc())
            .limit(3)
            .all()
        )
        if len(preferred_docs) >= 3:
            return preferred_docs

        preferred_ids = {doc.id for doc in preferred_docs}
        fallback_docs = (
            base_query.filter(KnowledgeDoc.id.notin_(preferred_ids) if preferred_ids else True)
            .order_by(KnowledgeDoc.updated_at.desc())
            .limit(3 - len(preferred_docs))
            .all()
        )
        return preferred_docs + fallback_docs

    return base_query.order_by(KnowledgeDoc.updated_at.desc()).limit(3).all()


def _summarize_content(content: str, max_length: int = 180) -> str:
    normalized = " ".join(content.split())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[:max_length]}..."


def _build_context(docs: list[KnowledgeDoc]) -> str:
    return "\n\n".join(
        f"【{index}. {doc.title}】\n{_summarize_content(doc.content, 260)}"
        for index, doc in enumerate(docs, start=1)
    )


def _build_answer(docs: list[KnowledgeDoc]) -> str:
    if not docs:
        return "当前知识库中暂未找到与该问题直接相关的政策资料，建议补充政策文档或咨询当地政务服务窗口。"

    titles = "\n".join(f"{index}. {doc.title}" for index, doc in enumerate(docs, start=1))
    summaries = "\n\n".join(
        f"{index}. {doc.title}：{_summarize_content(doc.content)}"
        for index, doc in enumerate(docs, start=1)
    )


def _normalize_category_id(value) -> int | None:
    if value in (None, "", 0, "0"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _build_retrieved_context(references: list[dict]) -> str | None:
    if not references:
        return None

    blocks = []
    for index, reference in enumerate(references, start=1):
        blocks.append(
            "\n".join(
                [
                    f"[参考资料 {index}]",
                    f"标题：{reference.get('title') or '未命名政策资料'}",
                    f"来源：{reference.get('source') or '未注明来源'}",
                    f"文档编号：{reference.get('document_id')}",
                    f"切片序号：{reference.get('chunk_index')}",
                    f"片段：{_summarize_content(reference.get('content') or '', 500)}",
                ]
            )
        )
    return "\n\n".join(blocks)


def _build_template_rag_answer(references: list[dict]) -> str:
    if not references:
        return "当前知识库中暂未找到与该问题直接相关的政策资料，建议补充政策文档或咨询当地政务服务窗口。"

    titles = "\n".join(
        f"{index}. {reference.get('title') or '未命名政策资料'}"
        for index, reference in enumerate(references, start=1)
    )
    summaries = "\n\n".join(
        (
            f"{index}. {reference.get('title') or '未命名政策资料'}："
            f"{_summarize_content(reference.get('content') or '', 260)}"
        )
        for index, reference in enumerate(references, start=1)
    )
    return (
        "根据知识库检索结果，系统找到以下与您问题相关的政策资料：\n\n"
        f"一、相关政策依据\n{titles}\n\n"
        f"二、主要内容\n{summaries}\n\n"
        "三、办理材料或处理建议\n"
        "请优先依据上述政策片段中明确列出的条件、材料和办理流程准备事项；"
        "如果片段未明确说明具体材料，请以政务服务窗口或官方办事指南为准。\n\n"
        "四、注意事项\n"
        "当前回答为知识库检索片段整理，不会补充知识库之外的细节。"
        "如政策存在地区差异或时效变化，请进一步核对当地最新要求。\n\n"
        "五、温馨提示：正式办理请以当地政务服务窗口或官方最新政策为准。"
    )


def _build_vector_references(question: str) -> list[dict]:
    try:
        search_result = vector_service.search_similar_chunks(question, limit=3)
    except Exception:
        return []

    references = []
    for item in search_result.results:
        metadata = item.metadata or {}
        references.append(
            {
                "document_id": item.document_id,
                "title": item.title,
                "chunk_index": item.chunk_index,
                "content": _summarize_content(item.content, 500),
                "distance": item.distance,
                "source": metadata.get("source") or None,
                "category_id": _normalize_category_id(metadata.get("category_id")),
            }
        )
    return references


def _build_keyword_references(docs: list[KnowledgeDoc]) -> list[dict]:
    return [
        {
            "document_id": doc.id,
            "title": doc.title,
            "chunk_index": 0,
            "content": _summarize_content(doc.content, 500),
            "distance": None,
            "source": doc.source,
            "category_id": doc.category_id,
        }
        for doc in docs
    ]
    return (
        "根据当前知识库中与您问题相关的政策资料，系统检索到以下信息：\n\n"
        f"相关政策资料：\n{titles}\n\n"
        f"内容摘要：\n{summaries}\n\n"
        "该回答为知识库检索结果生成，正式办理请以当地政务部门最新要求为准。"
    )


def answer_question(question: str, db: Session) -> ChatRecord:
    cleaned_question = question.strip()
    if not cleaned_question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    safety_result = detect_sensitive_info(cleaned_question)
    masked_question = (
        mask_sensitive_info(cleaned_question)
        if safety_result["has_sensitive_info"]
        else cleaned_question
    )
    safety_warning = build_safety_warning(safety_result)

    category = detect_category_by_question(masked_question, db)
    category_id = category.id if category else None

    references = _build_vector_references(masked_question)
    retrieval_mode = "vector" if references else "none"

    if not references:
        related_docs = _query_related_docs(masked_question, category_id, db)
        references = _build_keyword_references(related_docs)
        retrieval_mode = "keyword" if references else "none"

    retrieved_context = _build_retrieved_context(references)
    llm_result = llm_service.generate_answer_with_llm(
        masked_question,
        references,
        safety_warning,
    )
    if references and llm_result.get("success") and llm_result.get("answer"):
        ai_answer = llm_result["answer"]
        answer_mode = "llm_rag"
    else:
        ai_answer = _build_template_rag_answer(references)
        answer_mode = "template_rag" if references else "no_context"

    if safety_warning:
        ai_answer = f"{ai_answer}\n\n安全提示：{safety_warning}"

    record = ChatRecord(
        user_question=masked_question,
        retrieved_context=retrieved_context,
        ai_answer=ai_answer,
        category_id=category_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    record.masked_question = masked_question
    record.retrieval_mode = retrieval_mode
    record.references = references
    record.reference_count = len(references)
    record.answer_mode = answer_mode
    record.llm_provider = llm_result.get("provider")
    record.llm_model = llm_result.get("model")
    record.llm_error = llm_result.get("error")
    record.has_sensitive_info = safety_result["has_sensitive_info"]
    record.sensitive_types = safety_result["types"]
    record.safety_warning = safety_warning
    return record


def list_chat_history(db: Session, limit: int = 20) -> list[ChatRecord]:
    safe_limit = min(max(limit, 1), 100)
    return (
        db.query(ChatRecord)
        .order_by(ChatRecord.created_at.desc(), ChatRecord.id.desc())
        .limit(safe_limit)
        .all()
    )


def get_chat_record(db: Session, record_id: int) -> ChatRecord | None:
    return db.query(ChatRecord).filter(ChatRecord.id == record_id).first()
