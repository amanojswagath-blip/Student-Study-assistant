"""
Chat service using Groq API for fast LLM inference.
Provides context-aware Q&A without conversation history persistence.
"""

import logging
from typing import List, Dict, Any, Optional
import json

from app.core.config import settings
from app.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class ChatService:
    """Handles chat interactions using Groq API."""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.groq_client = None
        self._init_groq_client()
    
    def _init_groq_client(self):
        """Initialize Groq client if API key is available."""
        try:
            if hasattr(settings, 'GROQ_API_KEY') and settings.GROQ_API_KEY:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info("Groq client initialized")
            else:
                logger.warning("Groq API key not configured")
        except ImportError:
            logger.warning("Groq library not installed. Install with: pip install groq")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
    
    async def answer_question(
        self, 
        question: str, 
        document_ids: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate an answer to a question using document context."""
        
        try:
            # Handle casual conversation
            casual_responses = {
                'thanks': "You're welcome! Feel free to ask me any other questions about your documents.",
                'thank you': "You're very welcome! I'm here to help with any questions about your documents.",
                'good': "Great! Let me know if you have any other questions about your documents.",
                'ok': "Alright! Feel free to ask me anything else about your documents.",
                'hello': "Hello! I'm ready to help you with questions about your uploaded documents.",
                'hi': "Hi there! How can I help you analyze your documents today?"
            }
            
            question_lower = question.lower().strip()
            for casual_word, response in casual_responses.items():
                if question_lower in [casual_word, casual_word + '!', casual_word + '.']:
                    return {
                        "answer": response,
                        "sources": [],
                        "confidence": 1.0,
                        "chunks_used": 0
                    }
            
            # Search for relevant chunks
            relevant_chunks = await self.search_relevant_chunks(question, document_ids)
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find relevant information in your documents to answer that question. Please make sure your documents contain content related to your query.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Generate answer using Groq API
            answer = await self._generate_answer(question, relevant_chunks)
            
            # Clean up formatting and improve structure
            answer = self._clean_formatting(answer)
            answer = self._format_response_structure(answer)
            
            # Format sources
            sources = self._format_sources(relevant_chunks)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": min(len(relevant_chunks) / 3.0, 1.0),  # Simple confidence scoring
                "chunks_used": len(relevant_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def search_relevant_chunks(
        self, 
        question: str, 
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant document chunks with fallback options."""
        # First try regular search
        results = self.doc_processor.search_chunks(question, document_ids)
        
        if not results and question:
            logger.info(f"No results for '{question}', trying fallback searches...")
            
            # Try with individual words from the question
            question_words = [word.lower() for word in question.split() if len(word) > 2]
            for word in question_words:
                results = self.doc_processor.search_chunks(word, document_ids)
                if results:
                    logger.info(f"Found results using word '{word}'")
                    break
            
            # If still no results, try very broad searches
            if not results:
                broad_searches = ["summary", "main", "important", "key", "about", "topic"]
                for search_term in broad_searches:
                    results = self.doc_processor.search_chunks(search_term, document_ids)
                    if results:
                        logger.info(f"Found results using broad search '{search_term}'")
                        break
            
            # Last resort: return first few chunks of each document
            if not results:
                logger.info("No search matches found, returning first chunks from each document")
                target_docs = document_ids if document_ids else list(self.doc_processor.get_all_documents())
                
                for doc_id in target_docs:
                    chunks = self.doc_processor.get_document_chunks(doc_id)
                    if chunks:
                        # Add first few chunks with a default score
                        for chunk in chunks[:3]:  # First 3 chunks
                            chunk_with_score = chunk.copy()
                            chunk_with_score['score'] = 1  # Low score to indicate fallback
                            results.append(chunk_with_score)
                        
                        if len(results) >= 5:  # Limit total results
                            break
        
        return results
    
    async def _generate_answer(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """Generate answer using Groq API."""
        
        if not self.groq_client:
            return self._generate_fallback_answer(question, chunks)
        
        try:
            # Prepare context from chunks
            context = self._prepare_context(chunks)
            
            # Create system message
            system_message = """You are a helpful AI assistant that answers questions based on provided document context. 

Guidelines:
- Answer questions accurately based only on the provided context
- Use clean, well-formatted text without extra symbols like *** or **
- Write clear, organized responses with proper paragraph breaks
- Use bullet points with simple dashes (-) instead of asterisks
- If the context doesn't contain relevant information, say so clearly
- Be concise but comprehensive in your answers
- Include specific details when available
- For casual responses like "thanks", respond naturally without analyzing documents
- If asked about something not in the context, explain what information is missing
- Use a friendly, conversational tone suitable for students
- Format your response clearly with proper spacing between sections"""

            # Create user message with context and question
            user_message = f"""Here is the context from the user's documents:

{context}

Question: {question}

Please provide a clear, well-organized answer based on the context above. Use proper formatting with:
- Clear paragraph breaks
- Simple bullet points with dashes (-)  
- No extra asterisks or special characters
- Numbered lists where appropriate"""

            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Current supported production model
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.1,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return self._generate_fallback_answer(question, chunks)
    
    def _generate_fallback_answer(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """Generate a fallback answer when Groq API is unavailable."""
        if not chunks:
            return "I couldn't find relevant information in your documents to answer that question."
        
        # Simple keyword-based response generation
        context_text = " ".join([chunk['content'] for chunk in chunks[:3]])
        
        # Truncate context to reasonable length
        if len(context_text) > 800:
            context_text = context_text[:800] + "..."
        
        return f"""Based on your documents, here's the relevant information I found:

{context_text}

Note: Groq API is not available. For better AI-generated answers, please configure your GROQ_API_KEY in the .env file."""
    
    def _clean_formatting(self, text: str) -> str:
        """Clean up formatting issues in AI responses and improve readability."""
        import re
        
        # Remove excessive asterisks and stars
        text = re.sub(r'\*{2,}', '', text)  # Remove ** and more
        text = re.sub(r'\*\s*\*', '', text)  # Remove * *
        
        # Clean up bullet points - replace * with -
        text = re.sub(r'^\s*\*\s+', '- ', text, flags=re.MULTILINE)
        text = re.sub(r'\n\s*\*\s+', '\n- ', text)
        
        # Fix spacing around colons
        text = re.sub(r':\s*\*\s*', ': ', text)
        
        # Remove standalone asterisks
        text = re.sub(r'\s+\*\s+', ' ', text)
        text = re.sub(r'\*+', '', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s{3,}', ' ', text)
        
        # Improve paragraph breaks and spacing
        lines = text.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Add extra spacing after headings (lines ending with :)
            if line.endswith(':') and not line.startswith('-'):
                formatted_lines.append(line)
                formatted_lines.append('')  # Add blank line after headings
            
            # Add spacing before numbered items (1., 2., etc.)
            elif re.match(r'^\d+\.', line) and i > 0:
                if formatted_lines and formatted_lines[-1]:  # Don't add if already blank
                    formatted_lines.append('')
                formatted_lines.append(line)
            
            # Add spacing between bullet point sections
            elif line.startswith('-') and i > 0:
                prev_line = lines[i-1].strip() if i > 0 else ''
                if prev_line and not prev_line.startswith('-') and not prev_line.endswith(':'):
                    if formatted_lines and formatted_lines[-1]:
                        formatted_lines.append('')
                formatted_lines.append(line)
            
            # Regular lines
            else:
                formatted_lines.append(line)
        
        # Join with proper spacing
        text = '\n'.join(formatted_lines)
        
        # Ensure proper spacing between sections
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
        
        # Add spacing after numbered items that aren't followed by bullets
        text = re.sub(r'(\d+\.\s[^\n]+)\n([^-\s])', r'\1\n\n\2', text)
        
        # Ensure bullet points have consistent spacing
        text = re.sub(r'(\n-[^\n]+)\n([^-\s\n])', r'\1\n\n\2', text)
        
        return text.strip()
        
    def _format_response_structure(self, answer: str) -> str:
        """Add proper structure and spacing to the response."""
        # Split into paragraphs and format each section
        paragraphs = answer.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # Check if this is a heading (ends with : and is relatively short)
            if para.endswith(':') and len(para) <= 60 and '\n' not in para:
                formatted_paragraphs.append(f"**{para}**")
            
            # Check if this contains bullet points
            elif '-' in para and para.strip().startswith('-'):
                lines = para.split('\n')
                bullet_section = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('-'):
                        bullet_section.append(f"  {line}")  # Indent bullets slightly
                    else:
                        bullet_section.append(line)
                formatted_paragraphs.append('\n'.join(bullet_section))
            
            # Regular paragraph
            else:
                formatted_paragraphs.append(para)
        
        return '\n\n'.join(formatted_paragraphs)

    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Prepare context text from relevant chunks."""
        context_parts = []
        
        for i, chunk in enumerate(chunks[:5]):  # Use top 5 chunks
            # Get document info
            doc_info = self.doc_processor.get_document(chunk['document_id'])
            doc_name = doc_info.get('original_filename', 'Unknown') if doc_info else 'Unknown'
            
            context_part = f"""Document: {doc_name}
Content: {chunk['content'][:800]}{"..." if len(chunk['content']) > 800 else ""}
Keywords: {", ".join(chunk.get('keywords', []))}
---"""
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def _format_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source information from chunks."""
        sources = []
        seen_docs = set()
        
        for chunk in chunks[:3]:  # Show top 3 sources
            doc_info = self.doc_processor.get_document(chunk['document_id'])
            if doc_info and chunk['document_id'] not in seen_docs:
                sources.append({
                    "document": doc_info.get('original_filename', 'Unknown'),
                    "page": "N/A",  # Could be enhanced with page detection
                    "chunk_id": chunk['id'],
                    "relevance_score": chunk.get('score', 0),
                    "preview": chunk['content'][:150] + "..." if len(chunk['content']) > 150 else chunk['content']
                })
                seen_docs.add(chunk['document_id'])
        
        return sources
    
    def get_available_documents(self) -> List[Dict[str, Any]]:
        """Get list of available documents for chat."""
        return self.doc_processor.get_all_documents()
    
    def is_groq_available(self) -> bool:
        """Check if Groq API is available."""
        return self.groq_client is not None