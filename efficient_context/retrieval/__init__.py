"""
Retrieval components for efficient-context.
"""

from efficient_context.retrieval.base import BaseRetriever
from efficient_context.retrieval.cpu_optimized_retriever import CPUOptimizedRetriever

__all__ = ["BaseRetriever", "CPUOptimizedRetriever"]