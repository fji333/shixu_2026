from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ChatRecordBase(BaseModel):
    user_question: str
    retrieved_context: str | None = None
    ai_answer: str | None = None
    category_id: int | None = None


class ChatRecordCreate(ChatRecordBase):
    pass


class ChatRecordRead(ChatRecordBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(ChatRecordBase):
    id: int
    created_at: datetime
    masked_question: str | None = None
    retrieval_mode: str = "none"
    references: list[dict] = Field(default_factory=list)
    reference_count: int = 0
    answer_mode: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_error: str | None = None
    has_sensitive_info: bool = False
    sensitive_types: list[str] = Field(default_factory=list)
    safety_warning: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryItem(BaseModel):
    id: int
    user_question: str
    ai_answer: str | None = None
    category_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
