from app.config import settings


LLM_FALLBACK_MESSAGE = "大模型未启用或未配置，已使用模板式 RAG 回答"


def _clean_optional(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    return cleaned or None


def is_llm_available() -> bool:
    return all(
        [
            settings.llm_enable,
            _clean_optional(settings.llm_api_key),
            _clean_optional(settings.llm_base_url),
            _clean_optional(settings.llm_model),
        ]
    )


def build_government_rag_prompt(
    question: str,
    references: list[dict],
    safety_warning: str | None = None,
) -> str:
    reference_blocks = []
    for index, reference in enumerate(references, start=1):
        reference_blocks.append(
            "\n".join(
                [
                    f"[资料 {index}]",
                    f"标题：{reference.get('title') or '未命名政策资料'}",
                    f"来源：{reference.get('source') or '未注明来源'}",
                    f"内容：{reference.get('content') or ''}",
                ]
            )
        )

    safety_part = f"\n安全提醒：{safety_warning}" if safety_warning else ""
    return (
        "你是政务服务智能问答助手。\n"
        "只能基于检索到的政策资料回答用户问题，资料不足时不能编造。\n"
        "不要要求用户提交完整身份证号、手机号、银行卡号等敏感信息。\n"
        "回答应结构清晰，并提醒正式办理以当地政务服务窗口或官方最新政策为准。\n\n"
        f"用户问题：{question}{safety_part}\n\n"
        "检索到的政策资料：\n"
        f"{chr(10).join(reference_blocks) if reference_blocks else '暂无可用政策资料'}"
    )


def generate_answer_with_llm(
    question: str,
    references: list[dict],
    safety_warning: str | None = None,
) -> dict:
    provider = _clean_optional(settings.llm_provider)
    model = _clean_optional(settings.llm_model)

    if not is_llm_available():
        return {
            "success": False,
            "answer": None,
            "provider": provider,
            "model": model,
            "error": LLM_FALLBACK_MESSAGE,
        }

    build_government_rag_prompt(question, references, safety_warning)
    # TODO: 后续确定 DeepSeek、通义千问或其他 OpenAI-compatible API 后，
    # 在这里实现真实的大模型调用。当前阶段只预留接口，不发起外部请求。
    return {
        "success": False,
        "answer": None,
        "provider": provider,
        "model": model,
        "error": "大模型调用尚未实现，已使用模板式 RAG 回答",
    }
