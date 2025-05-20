"""
Semantic chunking for intelligent context segmentation.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple

from efficient_context.chunking.base import BaseChunker, Chunk
from efficient_context.utils.text import split_into_sentences, calculate_text_overlap

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticChunker(BaseChunker):
    """
    Chunker that creates chunks based on semantic boundaries.
    
    This chunker aims to keep semantically related content together, unlike
    simple token-based chunking that might split content mid-thought.
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        respect_paragraphs: bool = True,
        min_chunk_size: int = 100,
        max_chunk_size: int = 1024
    ):
        """
        Initialize the SemanticChunker.
        
        Args:
            chunk_size: Target size for chunks in tokens (words)
            chunk_overlap: Number of tokens to overlap between chunks
            respect_paragraphs: Whether to avoid breaking paragraphs across chunks
            min_chunk_size: Minimum chunk size in tokens
            max_chunk_size: Maximum chunk size in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.respect_paragraphs = respect_paragraphs
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        
        logger.info(
            "SemanticChunker initialized with target size: %d tokens, overlap: %d tokens",
            chunk_size, chunk_overlap
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in text.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            token_count: Estimated number of tokens
        """
        # Simple whitespace-based token estimation
        # This is much faster than using a tokenizer and good enough for chunking
        return len(text.split())
    
    def _identify_paragraphs(self, content: str) -> List[str]:
        """
        Split content into paragraphs.
        
        Args:
            content: Content to split
            
        Returns:
            paragraphs: List of paragraphs
        """
        # Split on empty lines (common paragraph separator)
        paragraphs = [p.strip() for p in content.split("\n\n")]
        
        # Handle other kinds of paragraph breaks and clean up
        result = []
        current = ""
        
        for p in paragraphs:
            # Skip empty paragraphs
            if not p:
                continue
                
            # Handle single newlines that might indicate paragraphs
            lines = p.split("\n")
            for line in lines:
                if not line.strip():
                    if current:
                        result.append(current)
                        current = ""
                else:
                    if current:
                        current += " " + line.strip()
                    else:
                        current = line.strip()
            
            if current:
                result.append(current)
                current = ""
        
        # Add any remaining content
        if current:
            result.append(current)
        
        return result if result else [content]
    
    def _create_semantic_chunks(
        self,
        paragraphs: List[str],
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Create chunks from paragraphs respecting semantic boundaries.
        
        Args:
            paragraphs: List of paragraphs to chunk
            document_id: Optional ID of the source document
            metadata: Optional metadata for the chunks
            
        Returns:
            chunks: List of Chunk objects
        """
        chunks = []
        current_chunk_text = ""
        current_token_count = 0
        
        for paragraph in paragraphs:
            paragraph_tokens = self._estimate_tokens(paragraph)
            
            # Check if adding this paragraph would exceed the max chunk size
            if (current_token_count + paragraph_tokens > self.max_chunk_size and 
                current_token_count >= self.min_chunk_size):
                # Create a new chunk with the current content
                chunk_id = str(uuid.uuid4())
                chunk = Chunk(
                    content=current_chunk_text.strip(),
                    chunk_id=chunk_id,
                    document_id=document_id,
                    metadata=metadata
                )
                chunks.append(chunk)
                
                # Start a new chunk with overlap
                if self.chunk_overlap > 0 and current_chunk_text:
                    # Get the last N tokens for overlap
                    words = current_chunk_text.split()
                    overlap_text = " ".join(words[-min(self.chunk_overlap, len(words)):])
                    current_chunk_text = overlap_text + " " + paragraph
                    current_token_count = self._estimate_tokens(current_chunk_text)
                else:
                    # No overlap
                    current_chunk_text = paragraph
                    current_token_count = paragraph_tokens
            # Handle very large paragraphs that exceed max_chunk_size on their own
            elif paragraph_tokens > self.max_chunk_size:
                # If we have existing content, create a chunk first
                if current_chunk_text:
                    chunk_id = str(uuid.uuid4())
                    chunk = Chunk(
                        content=current_chunk_text.strip(),
                        chunk_id=chunk_id,
                        document_id=document_id,
                        metadata=metadata
                    )
                    chunks.append(chunk)
                    current_chunk_text = ""
                    current_token_count = 0
                
                # Split the large paragraph into sentences
                sentences = split_into_sentences(paragraph)
                sentence_chunk = ""
                sentence_token_count = 0
                
                for sentence in sentences:
                    sentence_tokens = self._estimate_tokens(sentence)
                    
                    # Check if adding this sentence would exceed the max chunk size
                    if (sentence_token_count + sentence_tokens > self.max_chunk_size and 
                        sentence_token_count >= self.min_chunk_size):
                        # Create a new chunk with the current sentences
                        chunk_id = str(uuid.uuid4())
                        chunk = Chunk(
                            content=sentence_chunk.strip(),
                            chunk_id=chunk_id,
                            document_id=document_id,
                            metadata=metadata
                        )
                        chunks.append(chunk)
                        
                        # Start a new chunk with overlap
                        if self.chunk_overlap > 0 and sentence_chunk:
                            words = sentence_chunk.split()
                            overlap_text = " ".join(words[-min(self.chunk_overlap, len(words)):])
                            sentence_chunk = overlap_text + " " + sentence
                            sentence_token_count = self._estimate_tokens(sentence_chunk)
                        else:
                            sentence_chunk = sentence
                            sentence_token_count = sentence_tokens
                    else:
                        # Add the sentence to the current chunk
                        if sentence_chunk:
                            sentence_chunk += " " + sentence
                        else:
                            sentence_chunk = sentence
                        sentence_token_count += sentence_tokens
                
                # Add any remaining sentence content as a chunk
                if sentence_chunk:
                    chunk_id = str(uuid.uuid4())
                    chunk = Chunk(
                        content=sentence_chunk.strip(),
                        chunk_id=chunk_id,
                        document_id=document_id,
                        metadata=metadata
                    )
                    chunks.append(chunk)
            else:
                # Add the paragraph to the current chunk
                if current_chunk_text:
                    current_chunk_text += " " + paragraph
                else:
                    current_chunk_text = paragraph
                current_token_count += paragraph_tokens
                
                # Check if we've reached the target chunk size
                if current_token_count >= self.chunk_size:
                    chunk_id = str(uuid.uuid4())
                    chunk = Chunk(
                        content=current_chunk_text.strip(),
                        chunk_id=chunk_id,
                        document_id=document_id,
                        metadata=metadata
                    )
                    chunks.append(chunk)
                    
                    # Start a new chunk with overlap
                    if self.chunk_overlap > 0:
                        words = current_chunk_text.split()
                        current_chunk_text = " ".join(words[-min(self.chunk_overlap, len(words)):])
                        current_token_count = self._estimate_tokens(current_chunk_text)
                    else:
                        current_chunk_text = ""
                        current_token_count = 0
        
        # Add any remaining content as a final chunk
        if current_chunk_text and current_token_count >= self.min_chunk_size:
            chunk_id = str(uuid.uuid4())
            chunk = Chunk(
                content=current_chunk_text.strip(),
                chunk_id=chunk_id,
                document_id=document_id,
                metadata=metadata
            )
            chunks.append(chunk)
        
        return chunks
    
    def chunk(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None
    ) -> List[Chunk]:
        """
        Split content into semantic chunks.
        
        Args:
            content: Content to be chunked
            metadata: Optional metadata to associate with chunks
            document_id: Optional document ID to associate with chunks
            
        Returns:
            chunks: List of Chunk objects
        """
        if not content.strip():
            return []
            
        # Identify paragraphs
        if self.respect_paragraphs:
            paragraphs = self._identify_paragraphs(content)
        else:
            # Treat the whole content as one paragraph
            paragraphs = [content]
        
        # Create chunks from paragraphs
        chunks = self._create_semantic_chunks(paragraphs, document_id, metadata)
        
        logger.info("Created %d chunks from content", len(chunks))
        return chunks
