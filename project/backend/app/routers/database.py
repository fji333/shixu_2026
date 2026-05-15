from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import engine, get_db


router = APIRouter(prefix="/database", tags=["database"])

EXPECTED_TABLES = [
    "users",
    "categories",
    "knowledge_docs",
    "chat_records",
    "feedback",
]


@router.get("/ping")
def ping_database(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"数据库连接失败：{exc}") from exc

    return {
        "status": "ok",
        "message": "数据库连接正常",
    }


@router.get("/tables")
def list_database_tables() -> dict[str, list[str]]:
    try:
        current_tables = inspect(engine).get_table_names()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"读取数据库表失败：{exc}") from exc

    existing_tables = [table for table in EXPECTED_TABLES if table in current_tables]
    missing_tables = [table for table in EXPECTED_TABLES if table not in current_tables]

    return {
        "tables": existing_tables,
        "missing_tables": missing_tables,
    }
