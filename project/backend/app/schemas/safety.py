from pydantic import BaseModel, ConfigDict, Field


class SafetyCheckRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SafetyCheckResponse(BaseModel):
    original_text: str
    masked_text: str
    has_sensitive_info: bool
    sensitive_types: list[str]
    warnings: list[str]
    safety_warning: str | None = None

    model_config = ConfigDict(from_attributes=True)
