from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ChatRecord(Base):
    __tablename__ = "chat_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_question = Column(Text, nullable=False)
    retrieved_context = Column(Text, nullable=True)
    ai_answer = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    category = relationship("Category", back_populates="chat_records")
    feedback_items = relationship("Feedback", back_populates="chat_record")
