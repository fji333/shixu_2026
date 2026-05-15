from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.vector import (
    VectorRebuildResponse,
    VectorSearchResponse,
    VectorStatusResponse,
)
from app.services import vector_service


router = APIRouter(prefix="/vector", tags=["vector"])


@router.get("/status", response_model=VectorStatusResponse)
def get_vector_status(db: Session = Depends(get_db)):
    try:
        return vector_service.get_vector_status(db)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/search", response_model=VectorSearchResponse)
def search_vector(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=5, ge=1, le=20),
):
    try:
        return vector_service.search_similar_chunks(query, limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/rebuild", response_model=VectorRebuildResponse)
def rebuild_vector_index(db: Session = Depends(get_db)):
    try:
        return vector_service.rebuild_vector_index(db)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
