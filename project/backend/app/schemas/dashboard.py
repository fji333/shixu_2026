from datetime import datetime

from pydantic import BaseModel


class DashboardOverview(BaseModel):
    total_knowledge_docs: int
    active_knowledge_docs: int
    total_chat_records: int
    total_feedback: int
    helpful_feedback: int
    unhelpful_feedback: int
    neutral_feedback: int


class CategoryStatisticItem(BaseModel):
    category_id: int | None
    category_name: str | None
    chat_count: int
    knowledge_count: int


class RecentChatItem(BaseModel):
    id: int
    user_question: str
    ai_answer: str
    category_id: int | None
    created_at: datetime


class RecentFeedbackItem(BaseModel):
    id: int
    chat_id: int
    rating: str
    comment: str | None
    created_at: datetime


class DashboardResponse(BaseModel):
    overview: DashboardOverview
    category_statistics: list[CategoryStatisticItem]
    recent_chats: list[RecentChatItem]
    recent_feedback: list[RecentFeedbackItem]
