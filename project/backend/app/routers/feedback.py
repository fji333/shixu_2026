from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackStatistics
from app.services import feedback_service


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(feedback_data: FeedbackCreate, db: Session = Depends(get_db)):
    try:
        return feedback_service.create_feedback(db, feedback_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[FeedbackResponse])
def list_feedback(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return feedback_service.list_feedback(db, limit)


@router.get("/statistics", response_model=FeedbackStatistics)
def get_feedback_statistics(db: Session = Depends(get_db)):
    return feedback_service.get_feedback_statistics(db)
