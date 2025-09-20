<!-- Student Study Assistant - Python FastAPI Project -->

## Project Overview
Student Study Assistant with document processing, vector search, and Groq API integration for intelligent Q&A system.

## Tech Stack
- Backend: FastAPI (Python)
- Database: PostgreSQL with pgvector
- Document Processing: PyMuPDF, python-docx, spaCy
- Vector Search: sentence-transformers, scikit-learn
- AI: Groq API for fast LLM inference
- Frontend: Simple HTML/CSS/JS interface

## Key Features
- Document upload (PDF, DOCX, TXT)
- Intelligent chunking with keyword extraction
- Semantic search and context retrieval
- Context-aware Q&A using Groq API
- Source attribution and document references

## Development Guidelines
- Use async/await for FastAPI endpoints
- Implement proper error handling and logging
- Follow Python PEP 8 style guidelines
- Use type hints throughout the codebase
- Write comprehensive docstrings for functions
- Implement proper security for file uploads