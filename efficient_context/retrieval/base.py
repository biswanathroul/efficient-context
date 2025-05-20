"""
Base classes for retrieval components.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from efficient_context.chunking.base import Chunk

class BaseRetriever(ABC):
    """Base class for content retrieval components."""
    
    @abstractmethod
    def index_chunks(self, chunks: List[Chunk]) -> None:
        """
        Index chunks for future retrieval.
        
        Args:
            chunks: Chunks to index
        """
        pass
    
    @abstractmethod
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Chunk]:
        """
        Retrieve chunks relevant to a query.
        
        Args:
            query: Query to retrieve chunks for
            top_k: Number of chunks to retrieve
            
        Returns:
            chunks: List of retrieved chunks
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all indexed chunks."""
        pass
