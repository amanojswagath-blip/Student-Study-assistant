"""
Database configuration for Student Study Assistant.

Note: This application uses in-memory processing instead of a database 
for simplicity. This module is kept for potential future database integration.
"""

import logging

logger = logging.getLogger(__name__)

# Placeholder for future database integration
# Currently using in-memory processing in services/document_processor.py

class InMemoryStorage:
    """Simple in-memory storage for documents and chunks."""
    
    def __init__(self):
        self.documents = {}
        self.chunks = {}
        logger.info("In-memory storage initialized")
    
    def store_document(self, doc_id: str, document: dict):
        """Store a document in memory."""
        self.documents[doc_id] = document
    
    def get_document(self, doc_id: str):
        """Retrieve a document from memory."""
        return self.documents.get(doc_id)
    
    def store_chunks(self, doc_id: str, chunks: list):
        """Store document chunks in memory."""
        self.chunks[doc_id] = chunks
    
    def get_chunks(self, doc_id: str):
        """Retrieve document chunks from memory."""
        return self.chunks.get(doc_id, [])
    
    def clear(self):
        """Clear all stored data."""
        self.documents.clear()
        self.chunks.clear()
        logger.info("In-memory storage cleared")


# Global storage instance
storage = InMemoryStorage()


def get_storage():
    """Get the in-memory storage instance."""
    return storage