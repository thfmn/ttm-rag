"""
Document chunking module for RAG system.

This module provides functionality to split documents into smaller chunks
suitable for embedding generation and retrieval.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
import re
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChunkConfig:
    """Configuration for document chunking."""
    chunk_size: int = 512  # Characters per chunk
    chunk_overlap: int = 50  # Overlap between chunks
    min_chunk_size: int = 100  # Minimum chunk size
    preserve_sentences: bool = True  # Try to preserve sentence boundaries
    preserve_paragraphs: bool = False  # Try to preserve paragraph boundaries


class DocumentChunk(BaseModel):
    """Represents a single document chunk."""
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
    
    def generate_id(self) -> str:
        """Generate unique ID for the chunk."""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()[:8]
        return f"{self.document_id}_{self.chunk_index}_{content_hash}"


class DocumentChunker:
    """Handles document chunking for RAG processing."""
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        """
        Initialize the document chunker.
        
        Args:
            config: Chunking configuration
        """
        self.config = config or ChunkConfig()
        logger.info(f"Initialized DocumentChunker with config: {self.config}")
    
    def chunk_text(self, text: str, document_id: str, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """
        Split a text document into chunks.
        
        Args:
            text: Text to chunk
            document_id: ID of the source document
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of document chunks
        """
        if not text:
            logger.warning(f"Empty text provided for document {document_id}")
            return []
        
        if metadata is None:
            metadata = {}
        chunks = []
        
        # Clean and normalize text
        text = self._normalize_text(text)
        
        if self.config.preserve_sentences:
            # Split by sentences first
            sentences = self._split_sentences(text)
            chunks = self._chunk_sentences(sentences, document_id, metadata)
        else:
            # Simple character-based chunking
            chunks = self._chunk_by_characters(text, document_id, metadata)
        
        logger.info(f"Created {len(chunks)} chunks for document {document_id}")
        return chunks
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent chunking.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved for Thai text)
        # This handles common sentence endings
        sentence_endings = r'[.!?।။។။။]'
        
        # Split by sentence endings but keep the delimiter
        sentences = re.split(f'({sentence_endings})', text)
        
        # Recombine sentences with their delimiters
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
                if sentence.strip():
                    result.append(sentence.strip())
        
        # Add last sentence if it doesn't have a delimiter
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())
        
        return result if result else [text]
    
    def _chunk_sentences(self, sentences: List[str], document_id: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Create chunks from sentences while respecting size limits.
        
        Args:
            sentences: List of sentences
            document_id: Document ID
            metadata: Chunk metadata
            
        Returns:
            List of document chunks
        """
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        char_offset = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # Check if adding this sentence would exceed chunk size
            if current_size + sentence_size > self.config.chunk_size and current_chunk:
                # Create chunk from current sentences
                chunk_text = ' '.join(current_chunk)
                chunk = DocumentChunk(
                    chunk_id="",
                    document_id=document_id,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    start_char=char_offset,
                    end_char=char_offset + len(chunk_text),
                    metadata=metadata
                )
                chunk.chunk_id = chunk.generate_id()
                chunks.append(chunk)
                
                # Handle overlap
                if self.config.chunk_overlap > 0:
                    # Keep last few sentences for overlap
                    overlap_text = ' '.join(current_chunk[-2:])  # Keep last 2 sentences
                    if len(overlap_text) <= self.config.chunk_overlap * 2:
                        current_chunk = current_chunk[-2:]
                        current_size = len(' '.join(current_chunk))
                    else:
                        current_chunk = []
                        current_size = 0
                else:
                    current_chunk = []
                    current_size = 0
                
                char_offset = chunks[-1].end_char
                chunk_index += 1
            
            current_chunk.append(sentence)
            current_size += sentence_size + 1  # +1 for space
        
        # Add remaining sentences as final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) >= self.config.min_chunk_size:
                chunk = DocumentChunk(
                    chunk_id="",
                    document_id=document_id,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    start_char=char_offset,
                    end_char=char_offset + len(chunk_text),
                    metadata=metadata
                )
                chunk.chunk_id = chunk.generate_id()
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_characters(self, text: str, document_id: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Create chunks based on character count.
        
        Args:
            text: Text to chunk
            document_id: Document ID
            metadata: Chunk metadata
            
        Returns:
            List of document chunks
        """
        chunks = []
        chunk_index = 0
        
        for i in range(0, len(text), self.config.chunk_size - self.config.chunk_overlap):
            chunk_start = i
            chunk_end = min(i + self.config.chunk_size, len(text))
            chunk_text = text[chunk_start:chunk_end]
            
            if len(chunk_text) >= self.config.min_chunk_size:
                chunk = DocumentChunk(
                    chunk_id="",
                    document_id=document_id,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    start_char=chunk_start,
                    end_char=chunk_end,
                    metadata=metadata
                )
                chunk.chunk_id = chunk.generate_id()
                chunks.append(chunk)
                chunk_index += 1
        
        return chunks
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """
        Process multiple documents into chunks.
        
        Args:
            documents: List of documents with 'id', 'content', and optional 'metadata'
            
        Returns:
            List of all document chunks
        """
        all_chunks = []
        
        for doc in documents:
            doc_id = doc.get('id', '')
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            if not doc_id or not content:
                logger.warning(f"Skipping document with missing id or content")
                continue
            
            chunks = self.chunk_text(content, doc_id, metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"Processed {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks
