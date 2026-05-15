from fastapi import APIRouter

from app.config import settings
from app.services import llm_service


router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/status")
def get_llm_status():
    return {
        "enabled": settings.llm_enable,
        "available": llm_service.is_llm_available(),
        "provider": settings.llm_provider or None,
        "model": settings.llm_model or None,
        "base_url_configured": bool(settings.llm_base_url.strip()),
        "api_key_configured": bool(settings.llm_api_key.strip()),
    }
