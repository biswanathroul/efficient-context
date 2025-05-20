"""
Base classes for context compression components.
"""

from abc import ABC, abstractmethod
from typing import Optional

class BaseCompressor(ABC):
    """Base class for content compression components."""
    
    @abstractmethod
    def compress(self, content: str, target_size: Optional[int] = None) -> str:
        """
        Compress content to reduce size while preserving key information.
        
        Args:
            content: The content to compress
            target_size: Optional target size for the compressed content
            
        Returns:
            compressed_content: The compressed content
        """
        pass
