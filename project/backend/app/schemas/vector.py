from pydantic import BaseModel


class VectorSearchItem(BaseModel):
    document_id: int
    title: str | None
    chunk_index: int
    content: str
    distance: float | None = None
    metadata: dict


class VectorSearchResponse(BaseModel):
    query: str
    total: int
    results: list[VectorSearchItem]
    message: str | None = None


class VectorStatusResponse(BaseModel):
    chunk_count: int
    vector_count: int
    collection_name: str
    vector_db_path: str


class VectorRebuildResponse(BaseModel):
    document_count: int
    chunk_count: int
    vector_count: int
    collection_name: str
    vector_db_path: str
    message: str
