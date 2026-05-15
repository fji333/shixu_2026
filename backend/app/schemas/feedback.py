from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


FeedbackRating = Literal["helpful", "unhelpful", "neutral"]


class FeedbackCreate(BaseModel):
    chat_id: int
    rating: FeedbackRating
    comment: str | None = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    id: int
    chat_id: int
    rating: FeedbackRating
    comment: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackStatistics(BaseModel):
    total: int
    helpful_count: int
    unhelpful_count: int
    neutral_count: int
