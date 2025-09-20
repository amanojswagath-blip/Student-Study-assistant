"""
Document-related data schemas.
"""

from typing import List, Optional, Any, Dict
from datetime import datetime


# Simple data classes for API responses
class DocumentResponse:
    """Response schema for document operations."""
    
    def __init__(
        self,
        id: str,
        filename: str,
        original_filename: str,
        file_type: str,
        file_size: int,
        status: str,
        chunk_count: int,
        created_at: float,
        processed_at: Optional[float] = None,
        **kwargs
    ):
        self.id = id
        self.filename = filename
        self.original_filename = original_filename
        self.file_type = file_type
        self.file_size = file_size
        self.status = status
        self.chunk_count = chunk_count
        self.created_at = created_at
        self.processed_at = processed_at


class DocumentChunkResponse:
    """Response schema for document chunks."""
    
    def __init__(
        self,
        id: str,
        document_id: str,
        content: str,
        chunk_index: int,
        keywords: List[str],
        start_pos: int,
        end_pos: int,
        score: Optional[float] = None,
        **kwargs
    ):
        self.id = id
        self.document_id = document_id
        self.content = content
        self.chunk_index = chunk_index
        self.keywords = keywords
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.score = score


# For compatibility, also create dict-based versions
def document_response_dict(doc_info: Dict[str, Any]) -> Dict[str, Any]:
    """Convert document info to response dict."""
    return {
        "id": doc_info.get("id"),
        "filename": doc_info.get("filename"),
        "original_filename": doc_info.get("original_filename"),
        "file_type": doc_info.get("file_type"),
        "file_size": doc_info.get("file_size"),
        "status": doc_info.get("status"),
        "chunk_count": doc_info.get("chunk_count", 0),
        "created_at": doc_info.get("created_at"),
        "processed_at": doc_info.get("processed_at")
    }


def chunk_response_dict(chunk_info: Dict[str, Any]) -> Dict[str, Any]:
    """Convert chunk info to response dict."""
    return {
        "id": chunk_info.get("id"),
        "document_id": chunk_info.get("document_id"),
        "content": chunk_info.get("content"),
        "chunk_index": chunk_info.get("chunk_index"),
        "keywords": chunk_info.get("keywords", []),
        "start_pos": chunk_info.get("start_pos"),
        "end_pos": chunk_info.get("end_pos"),
        "score": chunk_info.get("score")
    }