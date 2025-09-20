"""
Document management endpoints for upload, processing, and retrieval.
Simplified in-memory version without database persistence.
"""

import logging
import os
import json
from typing import List, Optional
from uuid import uuid4

from app.core.config import settings
from app.services.document_processor import DocumentProcessor
from app.schemas.document import document_response_dict, chunk_response_dict

logger = logging.getLogger(__name__)

# Initialize document processor
doc_processor = DocumentProcessor()

try:
    from fastapi import APIRouter, File, HTTPException, UploadFile
    from fastapi.responses import JSONResponse
    
    router = APIRouter()

    @router.post("/upload")
    async def upload_document(file: UploadFile = File(...)):
        """Upload and process a document."""
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > getattr(settings, 'MAX_FILE_SIZE', 50 * 1024 * 1024):
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {getattr(settings, 'MAX_FILE_SIZE', 50 * 1024 * 1024)} bytes"
            )
        
        try:
            # Generate unique filename
            file_id = str(uuid4())
            filename = f"{file_id}{file_extension}"
            upload_dir = getattr(settings, 'UPLOAD_DIR', './uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # Process document
            document = await doc_processor.process_document(
                file_path=file_path,
                original_filename=file.filename
            )
            
            logger.info(f"Document uploaded and processed: {file.filename}")
            
            return JSONResponse(content=document_response_dict(document))
            
        except Exception as e:
            logger.error(f"Error processing document {file.filename}: {e}")
            raise HTTPException(status_code=500, detail="Error processing document")

    @router.get("/")
    async def list_documents(skip: int = 0, limit: int = 100):
        """List all uploaded documents."""
        try:
            documents = doc_processor.get_all_documents()
            # Apply pagination
            paginated_docs = documents[skip:skip + limit]
            return JSONResponse(content=[document_response_dict(doc) for doc in paginated_docs])
            
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            raise HTTPException(status_code=500, detail="Error fetching documents")

    @router.get("/{document_id}")
    async def get_document(document_id: str):
        """Get details of a specific document."""
        try:
            document = doc_processor.get_document(document_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            return JSONResponse(content=document_response_dict(document))
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching document {document_id}: {e}")
            raise HTTPException(status_code=500, detail="Error fetching document")

    @router.get("/{document_id}/chunks")
    async def get_document_chunks(document_id: str):
        """Get all chunks for a specific document."""
        try:
            chunks = doc_processor.get_document_chunks(document_id)
            return JSONResponse(content=[chunk_response_dict(chunk) for chunk in chunks])
            
        except Exception as e:
            logger.error(f"Error fetching chunks for document {document_id}: {e}")
            raise HTTPException(status_code=500, detail="Error fetching document chunks")

    @router.delete("/{document_id}")
    async def delete_document(document_id: str):
        """Delete a document and all its chunks."""
        try:
            success = doc_processor.delete_document(document_id)
            if not success:
                raise HTTPException(status_code=404, detail="Document not found")
            
            return JSONResponse(content={"message": "Document deleted successfully"})
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise HTTPException(status_code=500, detail="Error deleting document")

except ImportError:
    # Fallback router for development without FastAPI
    class Router:
        def post(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        def get(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        def delete(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    
    router = Router()
    
    async def upload_document(**kwargs):
        return {"error": "FastAPI not available"}
    
    async def list_documents(**kwargs):
        return {"error": "FastAPI not available"}
    
    async def get_document(**kwargs):
        return {"error": "FastAPI not available"}
    
    async def get_document_chunks(**kwargs):
        return {"error": "FastAPI not available"}
    
    async def delete_document(**kwargs):
        return {"error": "FastAPI not available"}