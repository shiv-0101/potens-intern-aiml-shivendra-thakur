from pydantic import BaseModel
from typing import Optional

class ChunkMetadata(BaseModel):
    source: str
    page: int
    chunk_id: int
    file_path: Optional[str] = None

class SearchResult(BaseModel):
    content: str
    metadata: ChunkMetadata
    similarity_score: float
    snippet: str