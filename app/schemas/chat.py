"""
Chat-related data schemas.
"""

from typing import List, Optional, Dict, Any


class ChatRequest:
    """Request schema for chat operations."""
    
    def __init__(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        **kwargs
    ):
        self.question = question
        self.document_ids = document_ids or []


class ChatResponse:
    """Response schema for chat operations."""
    
    def __init__(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        confidence: float = 0.0,
        chunks_used: int = 0,
        **kwargs
    ):
        self.answer = answer
        self.sources = sources
        self.confidence = confidence
        self.chunks_used = chunks_used


# Dict-based versions for compatibility
def chat_request_from_dict(data: Dict[str, Any]) -> ChatRequest:
    """Create ChatRequest from dictionary."""
    return ChatRequest(
        question=data.get("question", ""),
        document_ids=data.get("document_ids", [])
    )


def chat_response_dict(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert chat response to dictionary."""
    return {
        "answer": response_data.get("answer", ""),
        "sources": response_data.get("sources", []),
        "confidence": response_data.get("confidence", 0.0),
        "chunks_used": response_data.get("chunks_used", 0)
    }