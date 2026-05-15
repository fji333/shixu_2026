from fastapi import APIRouter

from app.schemas.safety import SafetyCheckRequest, SafetyCheckResponse
from app.services.safety_service import (
    build_safety_warning,
    detect_sensitive_info,
    mask_sensitive_info,
)


router = APIRouter(prefix="/safety", tags=["safety"])


@router.post("/check", response_model=SafetyCheckResponse)
def check_safety(request: SafetyCheckRequest):
    result = detect_sensitive_info(request.text)
    masked_text = mask_sensitive_info(request.text) if result["has_sensitive_info"] else request.text

    return SafetyCheckResponse(
        original_text=request.text,
        masked_text=masked_text,
        has_sensitive_info=result["has_sensitive_info"],
        sensitive_types=result["types"],
        warnings=result["warnings"],
        safety_warning=build_safety_warning(result),
    )
