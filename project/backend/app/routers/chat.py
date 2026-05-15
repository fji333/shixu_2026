from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatHistoryItem, ChatRequest, ChatResponse
from app.services import chat_service


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def create_chat(request: ChatRequest, db: Session = Depends(get_db)):
    return chat_service.answer_question(request.question, db)


@router.get("/history", response_model=list[ChatHistoryItem])
def list_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return chat_service.list_chat_history(db, limit)


@router.get("/{record_id}", response_model=ChatResponse)
def get_chat(record_id: int, db: Session = Depends(get_db)):
    record = chat_service.get_chat_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="问答记录不存在")
    return record
