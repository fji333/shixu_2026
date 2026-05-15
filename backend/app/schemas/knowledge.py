from datetime import datetime

from pydantic import BaseModel, ConfigDict


class KnowledgeBase(BaseModel):
    title: str
    category_id: int | None = None
    content: str
    source: str | None = None
    status: str = "active"


class KnowledgeCreate(KnowledgeBase):
    pass


class KnowledgeUpdate(BaseModel):
    title: str | None = None
    category_id: int | None = None
    content: str | None = None
    source: str | None = None
    status: str | None = None


class KnowledgeResponse(KnowledgeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeListResponse(BaseModel):
    id: int
    title: str
    category_id: int | None = None
    source: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


KnowledgeDocCreate = KnowledgeCreate
KnowledgeDocRead = KnowledgeResponse
