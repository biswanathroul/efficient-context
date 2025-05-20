"""
Base classes for context chunking components.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class Chunk:
    """Representation of a text chunk with metadata."""
    
    def __init__(
        self,
        content: str,
        chunk_id: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a chunk.
        
        Args:
            content: The text content of the chunk
            chunk_id: Unique identifier for the chunk
            document_id: Optional ID of the source document
            metadata: Optional metadata for the chunk
        """
        self.content = content
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.metadata = metadata or {}
        self.embedding = None

class BaseChunker(ABC):
    """Base class for content chunking components."""
    
    @abstractmethod
    def chunk(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None
    ) -> List[Chunk]:
        """
        Split content into chunks.
        
        Args:
            content: Content to be chunked
            metadata: Optional metadata to associate with chunks
            document_id: Optional document ID to associate with chunks
            
        Returns:
            chunks: List of Chunk objects
        """
        pass
