from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FileMetadata(BaseModel):
    id: Optional[str] = None
    filename: str
    file_path: str
    file_type: str
    file_size: int
    checksum: str
    created_at: datetime
    updated_at: datetime

class TextChunk(BaseModel):
    id: Optional[str] = None
    file_id: str
    chunk_text: str
    chunk_index: int
    created_at: datetime

class Embedding(BaseModel):
    id: Optional[str] = None
    chunk_id: str
    embedding: List[float]
    created_at: datetime

class SearchQuery(BaseModel):
    query: str
    limit: int = 5

class SearchResult(BaseModel):
    chunk_text: str
    file_name: str
    similarity_score: float 