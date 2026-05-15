from sqlalchemy.orm import Session

from app.models import Category, ChatRecord, Feedback, KnowledgeDoc
from app.schemas.dashboard import (
    CategoryStatisticItem,
    DashboardOverview,
    DashboardResponse,
    RecentChatItem,
    RecentFeedbackItem,
)


def _summarize_text(text: str | None, max_length: int = 150) -> str:
    if not text:
        return ""

    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[:max_length]}..."


def get_dashboard_data(db: Session) -> DashboardResponse:
    total_knowledge_docs = db.query(KnowledgeDoc).count()
    active_knowledge_docs = (
        db.query(KnowledgeDoc)
        .filter(KnowledgeDoc.status == "active")
        .count()
    )
    total_chat_records = db.query(ChatRecord).count()
    total_feedback = db.query(Feedback).count()
    helpful_feedback = db.query(Feedback).filter(Feedback.rating == "helpful").count()
    unhelpful_feedback = db.query(Feedback).filter(Feedback.rating == "unhelpful").count()
    neutral_feedback = db.query(Feedback).filter(Feedback.rating == "neutral").count()

    category_statistics = []
    categories = db.query(Category).order_by(Category.id.asc()).all()
    for category in categories:
        chat_count = (
            db.query(ChatRecord)
            .filter(ChatRecord.category_id == category.id)
            .count()
        )
        knowledge_count = (
            db.query(KnowledgeDoc)
            .filter(KnowledgeDoc.category_id == category.id)
            .count()
        )
        category_statistics.append(
            CategoryStatisticItem(
                category_id=category.id,
                category_name=category.name,
                chat_count=chat_count,
                knowledge_count=knowledge_count,
            )
        )

    recent_chat_records = (
        db.query(ChatRecord)
        .order_by(ChatRecord.created_at.desc(), ChatRecord.id.desc())
        .limit(5)
        .all()
    )
    recent_chats = [
        RecentChatItem(
            id=record.id,
            user_question=record.user_question,
            ai_answer=_summarize_text(record.ai_answer),
            category_id=record.category_id,
            created_at=record.created_at,
        )
        for record in recent_chat_records
    ]

    recent_feedback_records = (
        db.query(Feedback)
        .order_by(Feedback.created_at.desc(), Feedback.id.desc())
        .limit(5)
        .all()
    )
    recent_feedback = [
        RecentFeedbackItem(
            id=item.id,
            chat_id=item.chat_id,
            rating=item.rating,
            comment=item.comment,
            created_at=item.created_at,
        )
        for item in recent_feedback_records
    ]

    return DashboardResponse(
        overview=DashboardOverview(
            total_knowledge_docs=total_knowledge_docs,
            active_knowledge_docs=active_knowledge_docs,
            total_chat_records=total_chat_records,
            total_feedback=total_feedback,
            helpful_feedback=helpful_feedback,
            unhelpful_feedback=unhelpful_feedback,
            neutral_feedback=neutral_feedback,
        ),
        category_statistics=category_statistics,
        recent_chats=recent_chats,
        recent_feedback=recent_feedback,
    )
