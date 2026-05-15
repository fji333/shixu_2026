from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import KnowledgeDoc
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate


def list_knowledge_docs(
    db: Session,
    category_id: int | None = None,
    status: str | None = "active",
    keyword: str | None = None,
) -> list[KnowledgeDoc]:
    query = db.query(KnowledgeDoc)

    if category_id is not None:
        query = query.filter(KnowledgeDoc.category_id == category_id)
    if status:
        query = query.filter(KnowledgeDoc.status == status)
    if keyword:
        like_keyword = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                KnowledgeDoc.title.like(like_keyword),
                KnowledgeDoc.content.like(like_keyword),
            )
        )

    return query.order_by(KnowledgeDoc.id.desc()).all()


def search_knowledge_docs(db: Session, query_text: str) -> list[KnowledgeDoc]:
    like_keyword = f"%{query_text.strip()}%"
    return (
        db.query(KnowledgeDoc)
        .filter(
            KnowledgeDoc.status == "active",
            or_(
                KnowledgeDoc.title.like(like_keyword),
                KnowledgeDoc.content.like(like_keyword),
            ),
        )
        .order_by(KnowledgeDoc.id.desc())
        .all()
    )


def get_knowledge_doc(db: Session, doc_id: int) -> KnowledgeDoc | None:
    return db.query(KnowledgeDoc).filter(KnowledgeDoc.id == doc_id).first()


def get_knowledge_doc_by_title(db: Session, title: str) -> KnowledgeDoc | None:
    return db.query(KnowledgeDoc).filter(KnowledgeDoc.title == title).first()


def create_knowledge_doc(db: Session, data: KnowledgeCreate) -> KnowledgeDoc:
    doc = KnowledgeDoc(
        title=data.title.strip(),
        category_id=data.category_id,
        content=data.content.strip(),
        source=data.source,
        status=data.status or "active",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def update_knowledge_doc(
    db: Session,
    doc: KnowledgeDoc,
    data: KnowledgeUpdate,
) -> KnowledgeDoc:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(doc, field, value)

    doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)
    return doc


def soft_delete_knowledge_doc(db: Session, doc: KnowledgeDoc) -> KnowledgeDoc:
    doc.status = "inactive"
    doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)
    return doc
