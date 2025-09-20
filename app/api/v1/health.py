"""
Health check endpoints for monitoring system status.
"""

try:
    from fastapi import APIRouter
    from app.core.config import settings
    
    router = APIRouter()

    @router.get("/")
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "service": "student-study-assistant",
            "version": "1.0.0"
        }

    @router.get("/detailed")
    async def detailed_health_check():
        """Detailed health check with system information."""
        return {
            "status": "healthy",
            "service": "student-study-assistant", 
            "version": "1.0.0",
            "mode": "in-memory",
            "groq_api": "configured" if hasattr(settings, 'GROQ_API_KEY') and settings.GROQ_API_KEY else "not configured"
        }

except ImportError:
    # Fallback for development
    class Router:
        def get(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    
    router = Router()
    
    async def health_check():
        return {"status": "healthy", "service": "student-study-assistant"}
    
    async def detailed_health_check():
        return {"status": "healthy", "service": "student-study-assistant"}