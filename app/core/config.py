"""
Configuration management for Student Study Assistant.

This module handles all application settings and environment variables.
"""

import os
from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Fallback for environments without pydantic
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
                # Load from environment
                self.GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
                self.UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
                self.MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))
                self.EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
                self.CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
                self.CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
                self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
                self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
                self.BASE_DIR = Path(__file__).parent.parent.parent
                
                # Create upload directory
                upload_path = Path(self.UPLOAD_DIR)
                upload_path.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Groq API Configuration
    GROQ_API_KEY: str = ""
    
    # File Upload Configuration
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Vector Search Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_SEARCH_RESULTS: int = 5
    
    # Application Configuration
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create upload directory if it doesn't exist
        upload_path = Path(self.UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)


# Create global settings instance
try:
    settings = Settings()
except Exception:
    # Fallback settings
    settings = BaseSettings()
    if not hasattr(settings, 'GROQ_API_KEY'):
        settings.GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
        settings.UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
        settings.MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))
        settings.EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        settings.CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
        settings.CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
        settings.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        settings.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        settings.BASE_DIR = Path(__file__).parent.parent.parent