from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.config import PROJECT_ROOT, settings
from app.models import KnowledgeChunk, KnowledgeDoc
from app.schemas.vector import (
    VectorRebuildResponse,
    VectorSearchItem,
    VectorSearchResponse,
    VectorStatusResponse,
)
from app.services.embedding_service import embed_text, embed_texts
from app.services.text_splitter import split_text


COLLECTION_NAME = "gov_knowledge_chunks"


def get_vector_db_path() -> str:
    configured_path = Path(settings.vector_db_path)
    if configured_path.is_absolute():
        return str(configured_path)
    return str(PROJECT_ROOT / configured_path)


def _load_chromadb():
    try:
        import chromadb
    except ModuleNotFoundError as exc:
        raise RuntimeError("缺少 chromadb 依赖，请先安装 backend/requirements.txt") from exc
    return chromadb


def get_chroma_client():
    chromadb = _load_chromadb()
    vector_db_path = get_vector_db_path()
    Path(vector_db_path).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=vector_db_path)


def get_collection(create: bool = True):
    client = get_chroma_client()
    if create:
        return client.get_or_create_collection(name=COLLECTION_NAME)
    try:
        return client.get_collection(name=COLLECTION_NAME)
    except Exception:
        return None


def _reset_collection():
    client = get_chroma_client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    return client.get_or_create_collection(name=COLLECTION_NAME)


def rebuild_vector_index(db: Session) -> VectorRebuildResponse:
    active_docs = (
        db.query(KnowledgeDoc)
        .filter(KnowledgeDoc.status == "active")
        .order_by(KnowledgeDoc.id.asc())
        .all()
    )

    db.query(KnowledgeChunk).delete()
    db.commit()
    collection = _reset_collection()

    if not active_docs:
        return VectorRebuildResponse(
            document_count=0,
            chunk_count=0,
            vector_count=0,
            collection_name=COLLECTION_NAME,
            vector_db_path=get_vector_db_path(),
            message="知识库中暂无 active 文档，未生成向量索引",
        )

    vector_ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []
    chunk_count = 0

    for doc in active_docs:
        chunks = split_text(doc.content)
        for chunk_index, chunk_content in enumerate(chunks):
            vector_id = f"doc_{doc.id}_chunk_{chunk_index}"
            db.add(
                KnowledgeChunk(
                    document_id=doc.id,
                    chunk_index=chunk_index,
                    content=chunk_content,
                    vector_id=vector_id,
                )
            )
            vector_ids.append(vector_id)
            documents.append(chunk_content)
            metadatas.append(
                {
                    "document_id": doc.id,
                    "chunk_index": chunk_index,
                    "title": doc.title,
                    "category_id": doc.category_id or 0,
                    "source": doc.source or "",
                }
            )
            chunk_count += 1

    db.commit()

    if documents:
        collection.add(
            ids=vector_ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embed_texts(documents),
        )

    vector_count = collection.count()
    return VectorRebuildResponse(
        document_count=len(active_docs),
        chunk_count=chunk_count,
        vector_count=vector_count,
        collection_name=COLLECTION_NAME,
        vector_db_path=get_vector_db_path(),
        message="向量索引重建完成",
    )


def search_similar_chunks(query: str, limit: int = 5) -> VectorSearchResponse:
    cleaned_query = query.strip()
    if not cleaned_query:
        return VectorSearchResponse(query=query, total=0, results=[], message="检索关键词不能为空")

    collection = get_collection(create=False)
    if collection is None or collection.count() == 0:
        return VectorSearchResponse(
            query=cleaned_query,
            total=0,
            results=[],
            message="向量索引为空，请先运行 POST /vector/rebuild 或 scripts/build_vector_index.py",
        )

    safe_limit = min(max(limit, 1), 20)
    raw_result = collection.query(
        query_embeddings=[embed_text(cleaned_query)],
        n_results=safe_limit,
    )

    documents = raw_result.get("documents", [[]])[0]
    metadatas = raw_result.get("metadatas", [[]])[0]
    distances = raw_result.get("distances", [[]])[0]
    results = []

    for content, metadata, distance in zip(documents, metadatas, distances):
        metadata = metadata or {}
        results.append(
            VectorSearchItem(
                document_id=int(metadata.get("document_id", 0)),
                title=metadata.get("title"),
                chunk_index=int(metadata.get("chunk_index", 0)),
                content=content,
                distance=distance,
                metadata=metadata,
            )
        )

    return VectorSearchResponse(
        query=cleaned_query,
        total=len(results),
        results=results,
    )


def get_vector_status(db: Session) -> VectorStatusResponse:
    chunk_count = db.query(KnowledgeChunk).count()
    collection = get_collection(create=False)
    vector_count = collection.count() if collection is not None else 0
    return VectorStatusResponse(
        chunk_count=chunk_count,
        vector_count=vector_count,
        collection_name=COLLECTION_NAME,
        vector_db_path=get_vector_db_path(),
    )
