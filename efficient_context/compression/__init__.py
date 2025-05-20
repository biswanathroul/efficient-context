"""
Compression components for efficient-context.
"""

from efficient_context.compression.base import BaseCompressor
from efficient_context.compression.semantic_deduplicator import SemanticDeduplicator

__all__ = ["BaseCompressor", "SemanticDeduplicator"]