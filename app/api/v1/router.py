"""
Main API router for Student Study Assistant v1.

This module combines all API endpoints into a single router.
"""

try:
    from fastapi import APIRouter
    from app.api.v1 import documents, chat, health
    
    api_router = APIRouter()
    
    # Include all endpoint routers
    api_router.include_router(health.router, prefix="/health", tags=["health"])
    api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
    api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

except ImportError as e:
    # Fallback router for development
    class APIRouter:
        def include_router(self, *args, **kwargs):
            pass
    
    api_router = APIRouter()