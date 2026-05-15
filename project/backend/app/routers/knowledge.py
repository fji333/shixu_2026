from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeListResponse,
    KnowledgeResponse,
    KnowledgeUpdate,
)
from app.services import category_service, knowledge_service


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeListResponse])
def list_knowledge(
    category_id: int | None = None,
    status_value: str | None = Query(default="active", alias="status"),
    keyword: str | None = None,
    db: Session = Depends(get_db),
):
    return knowledge_service.list_knowledge_docs(
        db=db,
        category_id=category_id,
        status=status_value,
        keyword=keyword,
    )


@router.get("/search", response_model=list[KnowledgeListResponse])
def search_knowledge(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    if not query.strip():
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")

    return knowledge_service.search_knowledge_docs(db, query)


@router.get("/{doc_id}", response_model=KnowledgeResponse)
def get_knowledge(doc_id: int, db: Session = Depends(get_db)):
    doc = knowledge_service.get_knowledge_doc(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="知识文档不存在")
    return doc


@router.post("", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge(data: KnowledgeCreate, db: Session = Depends(get_db)):
    if not data.title or not data.title.strip():
        raise HTTPException(status_code=400, detail="知识文档标题不能为空")
    if not data.content or not data.content.strip():
        raise HTTPException(status_code=400, detail="知识文档正文不能为空")
    if data.category_id is not None and not category_service.get_category_by_id(db, data.category_id):
        raise HTTPException(status_code=400, detail="分类不存在")

    return knowledge_service.create_knowledge_doc(db, data)


@router.put("/{doc_id}", response_model=KnowledgeResponse)
def update_knowledge(
    doc_id: int,
    data: KnowledgeUpdate,
    db: Session = Depends(get_db),
):
    doc = knowledge_service.get_knowledge_doc(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="知识文档不存在")
    if data.category_id is not None and not category_service.get_category_by_id(db, data.category_id):
        raise HTTPException(status_code=400, detail="分类不存在")
    if data.title is not None and not data.title.strip():
        raise HTTPException(status_code=400, detail="知识文档标题不能为空")
    if data.content is not None and not data.content.strip():
        raise HTTPException(status_code=400, detail="知识文档正文不能为空")

    return knowledge_service.update_knowledge_doc(db, doc, data)


@router.delete("/{doc_id}")
def delete_knowledge(doc_id: int, db: Session = Depends(get_db)):
    doc = knowledge_service.get_knowledge_doc(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="知识文档不存在")

    knowledge_service.soft_delete_knowledge_doc(db, doc)
    return {
        "status": "ok",
        "message": "知识文档已删除",
    }
