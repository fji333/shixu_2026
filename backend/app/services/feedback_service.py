from sqlalchemy.orm import Session

from app.models import ChatRecord, Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackStatistics


def create_feedback(db: Session, feedback_data: FeedbackCreate) -> Feedback:
    chat_record = (
        db.query(ChatRecord)
        .filter(ChatRecord.id == feedback_data.chat_id)
        .first()
    )
    if not chat_record:
        raise ValueError("问答记录不存在，无法提交反馈")

    comment = feedback_data.comment.strip() if feedback_data.comment else None
    feedback = Feedback(
        chat_id=feedback_data.chat_id,
        rating=feedback_data.rating,
        comment=comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def list_feedback(db: Session, limit: int = 50) -> list[Feedback]:
    safe_limit = min(max(limit, 1), 100)
    return (
        db.query(Feedback)
        .order_by(Feedback.created_at.desc(), Feedback.id.desc())
        .limit(safe_limit)
        .all()
    )


def get_feedback_statistics(db: Session) -> FeedbackStatistics:
    total = db.query(Feedback).count()
    helpful_count = db.query(Feedback).filter(Feedback.rating == "helpful").count()
    unhelpful_count = db.query(Feedback).filter(Feedback.rating == "unhelpful").count()
    neutral_count = db.query(Feedback).filter(Feedback.rating == "neutral").count()

    return FeedbackStatistics(
        total=total,
        helpful_count=helpful_count,
        unhelpful_count=unhelpful_count,
        neutral_count=neutral_count,
    )
