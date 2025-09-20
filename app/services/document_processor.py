"""
In-memory document processing service with simple file-based persistence.
Processes documents and saves them to JSON files for persistence across server restarts.
"""

import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

# In-memory storage for documents and chunks
documents_store: Dict[str, Dict[str, Any]] = {}
chunks_store: Dict[str, List[Dict[str, Any]]] = {}

# Persistence directory
PERSISTENCE_DIR = Path("data/documents")
DOCUMENTS_FILE = PERSISTENCE_DIR / "documents.json"
CHUNKS_DIR = PERSISTENCE_DIR / "chunks"

def _ensure_persistence_dirs():
    """Ensure persistence directories exist."""
    PERSISTENCE_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

def _save_documents_index():
    """Save documents index to file."""
    try:
        _ensure_persistence_dirs()
        with open(DOCUMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(documents_store, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving documents index: {e}")

def _load_documents_index():
    """Load documents index from file."""
    global documents_store
    try:
        if DOCUMENTS_FILE.exists():
            with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
                documents_store = json.load(f)
                logger.info(f"Loaded {len(documents_store)} documents from persistence")
    except Exception as e:
        logger.error(f"Error loading documents index: {e}")
        documents_store = {}

def _save_document_chunks(doc_id: str, chunks: List[Dict[str, Any]]):
    """Save chunks for a document."""
    try:
        _ensure_persistence_dirs()
        chunks_file = CHUNKS_DIR / f"{doc_id}.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving chunks for {doc_id}: {e}")

def _load_document_chunks(doc_id: str) -> List[Dict[str, Any]]:
    """Load chunks for a document."""
    try:
        chunks_file = CHUNKS_DIR / f"{doc_id}.json"
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading chunks for {doc_id}: {e}")
    return []

def _load_all_chunks():
    """Load all chunks into memory."""
    global chunks_store
    chunks_store = {}
    for doc_id in documents_store.keys():
        chunks = _load_document_chunks(doc_id)
        if chunks:
            chunks_store[doc_id] = chunks
    logger.info(f"Loaded chunks for {len(chunks_store)} documents")

# Load persisted data on module import
_load_documents_index()
_load_all_chunks()


class DocumentProcessor:
    """Handles document processing and chunking without database persistence."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.docx', '.txt', '.md'}
    
    async def process_document(self, file_path: str, original_filename: str, **kwargs) -> Dict[str, Any]:
        """Process a document and create chunks."""
        try:
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Extract text from document
            text_content = await self._extract_text(file_path)
            
            # Create chunks
            chunks = await self._create_chunks(text_content, doc_id)
            
            # Get file info
            file_stat = os.stat(file_path)
            file_extension = Path(file_path).suffix.lower()
            
            # Store document info
            document_info = {
                "id": doc_id,
                "filename": os.path.basename(file_path),
                "original_filename": original_filename,
                "file_type": file_extension,
                "file_size": file_stat.st_size,
                "status": "processed",
                "chunk_count": len(chunks),
                "created_at": file_stat.st_ctime,
                "processed_at": file_stat.st_mtime,
                "content": text_content[:1000] + "..." if len(text_content) > 1000 else text_content
            }
            
            # Store in memory and persistence
            documents_store[doc_id] = document_info
            chunks_store[doc_id] = chunks
            
            # Save to persistence
            _save_documents_index()
            _save_document_chunks(doc_id, chunks)
            
            logger.info(f"Processed document: {original_filename} ({len(chunks)} chunks) - SAVED TO PERSISTENCE")
            
            return document_info
            
        except Exception as e:
            logger.error(f"Error processing document {original_filename}: {e}")
            raise
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from various document formats."""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.txt' or file_extension == '.md':
            return await self._extract_text_file(file_path)
        elif file_extension == '.pdf':
            return await self._extract_pdf(file_path)
        elif file_extension == '.docx':
            return await self._extract_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    async def _extract_text_file(self, file_path: str) -> str:
        """Extract text from plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    async def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF files."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            logger.warning("PyMuPDF not installed. PDF processing limited.")
            return f"PDF file: {os.path.basename(file_path)} (Text extraction requires PyMuPDF)"
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            return f"Error extracting PDF content: {str(e)}"
    
    async def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX files."""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            logger.warning("python-docx not installed. DOCX processing limited.")
            return f"DOCX file: {os.path.basename(file_path)} (Text extraction requires python-docx)"
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            return f"Error extracting DOCX content: {str(e)}"
    
    async def _create_chunks(self, text: str, doc_id: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Create text chunks from document content."""
        if not text.strip():
            return []
        
        chunks = []
        text_length = len(text)
        start = 0
        chunk_index = 0
        
        while start < text_length:
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < text_length:
                # Look for sentence endings near the chunk boundary
                for punct in ['. ', '! ', '? ', '\n\n']:
                    punct_pos = text.rfind(punct, start + chunk_size - 200, end)
                    if punct_pos > start + chunk_size // 2:  # Don't make chunks too small
                        end = punct_pos + len(punct)
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                # Extract keywords (simple approach)
                keywords = await self._extract_keywords(chunk_text)
                
                chunk = {
                    "id": f"{doc_id}_chunk_{chunk_index}",
                    "document_id": doc_id,
                    "content": chunk_text,
                    "chunk_index": chunk_index,
                    "keywords": keywords,
                    "start_pos": start,
                    "end_pos": end,
                    "length": len(chunk_text)
                }
                chunks.append(chunk)
                chunk_index += 1
            
            # Move to next chunk with overlap
            start = max(start + chunk_size - overlap, end - overlap)
            if start >= text_length:
                break
        
        return chunks
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text chunk."""
        # Simple keyword extraction - can be improved with NLP libraries
        import re
        
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 
            'they', 'them', 'their', 'there', 'where', 'when', 'what', 'which', 'who', 'how',
            'can', 'may', 'must', 'shall', 'also', 'just', 'only', 'even', 'still',
            'now', 'then', 'here', 'very', 'more', 'most', 'much', 'many', 'some', 'any'
        }
        
        # Extract words (letters only, minimum 2 characters for better matching)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        
        # Filter out stop words and get unique words
        keywords = list(set(word for word in words if word not in stop_words))
        
        # Return top keywords (by frequency in this chunk)
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top 15 (more keywords for better matching)
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:15]]
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Get document info by ID."""
        # Ensure data is loaded
        if not documents_store and DOCUMENTS_FILE.exists():
            _load_documents_index()
            _load_all_chunks()
        return documents_store.get(doc_id)
    
    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document."""
        # Ensure data is loaded
        if not chunks_store and DOCUMENTS_FILE.exists():
            _load_documents_index()
            _load_all_chunks()
        return chunks_store.get(doc_id, [])
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents."""
        # Ensure data is loaded
        if not documents_store and DOCUMENTS_FILE.exists():
            _load_documents_index()
            _load_all_chunks()
        return list(documents_store.values())
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its chunks."""
        if doc_id in documents_store:
            del documents_store[doc_id]
            if doc_id in chunks_store:
                del chunks_store[doc_id]
            
            # Remove from persistence
            try:
                chunks_file = CHUNKS_DIR / f"{doc_id}.json"
                if chunks_file.exists():
                    chunks_file.unlink()
                _save_documents_index()
                logger.info(f"Deleted document {doc_id} from memory and persistence")
            except Exception as e:
                logger.error(f"Error deleting persisted data for {doc_id}: {e}")
            
            return True
        return False
    
    def search_chunks(self, query: str, document_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Simple text search in chunks."""
        results = []
        query_lower = query.lower()
        
        # Expand common search terms
        query_expansions = {
            'summarize': ['summary', 'main', 'key', 'important', 'conclusion', 'overview'],
            'summary': ['summarize', 'main', 'key', 'important', 'conclusion', 'overview'],
            'what': ['about', 'topic', 'subject', 'main', 'content'],
            'explain': ['about', 'description', 'definition', 'meaning'],
            'describe': ['about', 'description', 'explanation', 'details'],
            'overview': ['summary', 'main', 'introduction', 'about']
        }
        
        # Build expanded query terms
        expanded_terms = set(query_lower.split())
        for word in query_lower.split():
            if word in query_expansions:
                expanded_terms.update(query_expansions[word])
        
        # Get all relevant chunks
        target_docs = document_ids if document_ids else list(chunks_store.keys())
        
        logger.info(f"Searching for: '{query}' (expanded: {list(expanded_terms)}) across {len(target_docs)} documents")
        logger.info(f"Total chunks available: {sum(len(chunks_store.get(doc_id, [])) for doc_id in target_docs)}")
        
        for doc_id in target_docs:
            if doc_id in chunks_store:
                doc_chunks = chunks_store[doc_id]
                logger.info(f"Document {doc_id[:8]}... has {len(doc_chunks)} chunks")
                
                for chunk in doc_chunks:
                    # Simple scoring based on keyword matches and content relevance
                    score = 0
                    chunk_content = chunk['content'].lower()
                    
                    # Check for direct text matches with original query
                    if query_lower in chunk_content:
                        score += 5
                        logger.debug(f"Direct match found in chunk {chunk['id']} (score +5)")
                    
                    # Check for expanded term matches in content
                    for term in expanded_terms:
                        if term in chunk_content:
                            score += 3
                            logger.debug(f"Expanded term '{term}' found in content (score +3)")
                    
                    # Check for keyword matches
                    query_words = expanded_terms
                    chunk_keywords = set(chunk.get('keywords', []))
                    common_keywords = query_words.intersection(chunk_keywords)
                    score += len(common_keywords) * 2
                    if common_keywords:
                        logger.debug(f"Keyword matches in chunk {chunk['id']}: {common_keywords} (score +{len(common_keywords) * 2})")
                    
                    # Check for partial word matches
                    for word in query_words:
                        if len(word) > 3:  # Only check longer words
                            if any(word in keyword for keyword in chunk_keywords):
                                score += 1
                            # Also check if query word appears in content
                            if word in chunk_content:
                                score += 1
                    
                    # If no score yet but this is a common query, give it a base score
                    if score == 0 and query_lower in ['summarize', 'summary', 'what is this', 'main topic']:
                        score = 2  # Base score for common queries
                        logger.debug(f"Applied base score for common query: {query_lower}")
                    
                    if score > 0:
                        chunk_with_score = chunk.copy()
                        chunk_with_score['score'] = score
                        results.append(chunk_with_score)
                        logger.debug(f"Added chunk {chunk['id']} with score {score}")
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        logger.info(f"Search completed: found {len(results)} relevant chunks")
        
        if results:
            logger.info(f"Top result score: {results[0]['score']}")
        else:
            logger.warning(f"No relevant chunks found for query: '{query}'")
            # Debug: show what we have
            for doc_id in target_docs[:1]:  # Just check first doc
                if doc_id in chunks_store and chunks_store[doc_id]:
                    sample_chunk = chunks_store[doc_id][0]
                    logger.debug(f"Sample chunk content (first 200 chars): {sample_chunk['content'][:200]}")
                    logger.debug(f"Sample chunk keywords: {sample_chunk.get('keywords', [])[:10]}")
        
        return results[:5]  # Return top 5 results