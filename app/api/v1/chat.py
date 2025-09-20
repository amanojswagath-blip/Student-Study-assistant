"""
Chat endpoints for Q&A functionality using Groq API.
Simplified in-memory version without conversation persistence.
"""

import logging
import json
from typing import List, Dict, Any

from app.services.chat_service import ChatService
from app.schemas.chat import chat_request_from_dict, chat_response_dict

logger = logging.getLogger(__name__)

# Initialize chat service
chat_service = ChatService()

try:
    from fastapi import APIRouter, HTTPException, Request
    from fastapi.responses import JSONResponse
    
    router = APIRouter()

    @router.post("/ask")
    async def ask_question(request: Request):
        """Ask a question about uploaded documents."""
        try:
            # Parse request body
            body = await request.body()
            data = json.loads(body) if body else {}
            
            # Create request object
            chat_request = chat_request_from_dict(data)
            
            if not chat_request.question.strip():
                raise HTTPException(status_code=400, detail="Question cannot be empty")
            
            # Process question
            response = await chat_service.answer_question(
                question=chat_request.question,
                document_ids=chat_request.document_ids
            )
            
            return JSONResponse(content=chat_response_dict(response))
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in request body")
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error processing your question. Please try again."
            )

    @router.post("/debug-search")
    async def debug_search(request: Request):
        """Debug search functionality with detailed logging."""
        try:
            # Parse request body
            body = await request.body()
            data = json.loads(body) if body else {}
            
            query = data.get("question", "")
            if not query.strip():
                raise HTTPException(status_code=400, detail="Search query cannot be empty")
            
            # Get available documents
            available_docs = chat_service.get_available_documents()
            
            # Perform search with debug info
            chunks = await chat_service.search_relevant_chunks(query)
            
            debug_response = {
                "query": query,
                "available_documents": len(available_docs),
                "total_chunks_found": len(chunks),
                "chunks": []
            }
            
            for chunk in chunks[:3]:  # Show first 3 results
                debug_response["chunks"].append({
                    "chunk_id": chunk.get("id"),
                    "document_id": chunk.get("document_id"),
                    "score": chunk.get("score", 0),
                    "content_preview": chunk.get("content", "")[:300] + "...",
                    "keywords": chunk.get("keywords", []),
                    "chunk_index": chunk.get("chunk_index")
                })
            
            # Also include document info
            debug_response["documents"] = [
                {
                    "id": doc.get("id"),
                    "filename": doc.get("original_filename"),
                    "chunks": doc.get("chunk_count", 0)
                }
                for doc in available_docs
            ]
            
            return JSONResponse(content=debug_response)
            
        except Exception as e:
            logger.error(f"Error in debug search: {e}")
            return JSONResponse(content={"error": str(e), "traceback": str(e)})

    @router.post("/search")
    async def search_documents(request: Request):
        """Search for relevant document chunks without generating an answer."""
        try:
            # Parse request body
            body = await request.body()
            data = json.loads(body) if body else {}
            
            # Create request object
            chat_request = chat_request_from_dict(data)
            
            if not chat_request.question.strip():
                raise HTTPException(status_code=400, detail="Search query cannot be empty")
            
            # Search for chunks
            chunks = await chat_service.search_relevant_chunks(
                question=chat_request.question,
                document_ids=chat_request.document_ids
            )
            
            # Format response
            search_results = []
            for chunk in chunks:
                search_results.append({
                    "chunk_id": chunk.get("id"),
                    "document_id": chunk.get("document_id"),
                    "content": chunk.get("content", "")[:500] + ("..." if len(chunk.get("content", "")) > 500 else ""),
                    "score": chunk.get("score", 0),
                    "keywords": chunk.get("keywords", [])
                })
            
            return JSONResponse(content=search_results)
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in request body")
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error searching documents. Please try again."
            )

    @router.get("/debug")
    async def debug_chat_service():
        """Debug endpoint to check document processing status."""
        try:
            available_docs = chat_service.get_available_documents()
            
            debug_info = {
                "total_documents": len(available_docs),
                "groq_available": chat_service.is_groq_available(),
                "documents": []
            }
            
            for doc in available_docs:
                doc_id = doc.get("id")
                chunks = chat_service.doc_processor.get_document_chunks(doc_id)
                
                debug_info["documents"].append({
                    "id": doc_id,
                    "filename": doc.get("original_filename"),
                    "chunk_count": doc.get("chunk_count", 0),
                    "actual_chunks": len(chunks),
                    "file_size": doc.get("file_size", 0),
                    "status": doc.get("status"),
                    "sample_chunk": chunks[0].get("content", "")[:200] + "..." if chunks else "No chunks",
                    "sample_keywords": chunks[0].get("keywords", [])[:10] if chunks else []
                })
            
            return JSONResponse(content=debug_info)
            
        except Exception as e:
            logger.error(f"Error in debug endpoint: {e}")
            return JSONResponse(content={"error": str(e)})

    @router.get("/status")
    async def get_chat_status():
        """Get chat service status."""
        try:
            available_docs = chat_service.get_available_documents()
            groq_available = chat_service.is_groq_available()
            
            return JSONResponse(content={
                "status": "ready" if available_docs else "waiting_for_documents",
                "groq_available": groq_available,
                "available_documents": len(available_docs),
                "documents": [
                    {
                        "id": doc.get("id"),
                        "filename": doc.get("original_filename"),
                        "chunks": doc.get("chunk_count", 0)
                    }
                    for doc in available_docs
                ]
            })
            
        except Exception as e:
            logger.error(f"Error getting chat status: {e}")
            raise HTTPException(status_code=500, detail="Error getting chat status")

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
    
    router = Router()
    
    async def ask_question(**kwargs):
        return {"error": "FastAPI not available"}
    
    async def search_documents(**kwargs):
        return {"error": "FastAPI not available"}
    
    async def get_chat_status(**kwargs):
        return {"error": "FastAPI not available"}