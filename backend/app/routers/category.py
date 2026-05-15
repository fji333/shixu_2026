from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services import category_service


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return category_service.list_categories(db)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    if not data.name or not data.name.strip():
        raise HTTPException(status_code=400, detail="分类名称不能为空")

    name = data.name.strip()
    if category_service.get_category_by_name(db, name):
        raise HTTPException(status_code=400, detail="分类名称已存在")

    try:
        return category_service.create_category(
            db,
            CategoryCreate(name=name, description=data.description),
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="分类名称已存在") from exc
