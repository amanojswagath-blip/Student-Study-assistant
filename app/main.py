"""
Student Study Assistant - Main FastAPI Application

This is the main entry point for the Student Study Assistant application.
It provides document processing, vector search, and AI-powered Q&A capabilities.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    logger.info("Starting Student Study Assistant...")
    logger.info("In-memory mode - no database persistence")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Student Study Assistant...")


# Create FastAPI application
app = FastAPI(
    title="Student Study Assistant",
    description="AI-powered document processing and Q&A system for students",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files for frontend
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


@app.get("/")
async def root():
    """Serve the main HTML page."""
    try:
        return FileResponse("app/static/index.html")
    except:
        return {
            "message": "Student Study Assistant API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health"
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "student-study-assistant"}


if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.DEBUG
        )
    except ImportError:
        logger.error("uvicorn not installed. Install with: pip install uvicorn[standard]")