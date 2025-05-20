"""
CPU-optimized retrieval for efficient context handling.
"""

import logging
import heapq
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np

from efficient_context.retrieval.base import BaseRetriever
from efficient_context.chunking.base import Chunk

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CPUOptimizedRetriever(BaseRetriever):
    """
    Retriever optimized for CPU performance and low memory usage.
    
    This retriever uses techniques to minimize computational requirements
    while still providing high-quality retrieval results.
    """
    
    def __init__(
        self,
        embedding_model: str = "lightweight",
        similarity_metric: str = "cosine",
        use_batching: bool = True,
        batch_size: int = 32,
        max_index_size: Optional[int] = None,
    ):
        """
        Initialize the CPUOptimizedRetriever.
        
        Args:
            embedding_model: Model to use for embeddings
            similarity_metric: Metric for comparing embeddings
            use_batching: Whether to batch embedding operations
            batch_size: Size of batches for embedding
            max_index_size: Maximum number of chunks to keep in the index
        """
        self.embedding_model = embedding_model
        self.similarity_metric = similarity_metric
        self.use_batching = use_batching
        self.batch_size = batch_size
        self.max_index_size = max_index_size
        
        # Initialize storage
        self.chunks = []
        self.chunk_embeddings = None
        self.chunk_ids_to_index = {}
        
        # Initialize the embedding model
        self._init_embedding_model()
        
        logger.info("CPUOptimizedRetriever initialized with model: %s", embedding_model)
    
    def _init_embedding_model(self):
        """Initialize the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Choose a lightweight model for CPU efficiency
            if self.embedding_model == "lightweight":
                # MiniLM models are lightweight and efficient
                self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
            else:
                # Default to a balanced model
                self.model = SentenceTransformer(self.embedding_model)
                
            logger.info("Using embedding model: %s", self.model.get_sentence_embedding_dimension())
        except ImportError:
            logger.warning("SentenceTransformer not available, using numpy fallback (less accurate)")
            self.model = None
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            embeddings: Array of text embeddings
        """
        if not texts:
            return np.array([])
            
        if self.model is not None:
            # Use the sentence transformer if available
            # Apply batching for memory efficiency
            if self.use_batching and len(texts) > self.batch_size:
                embeddings = []
                
                for i in range(0, len(texts), self.batch_size):
                    batch = texts[i:i+self.batch_size]
                    batch_embeddings = self.model.encode(
                        batch,
                        show_progress_bar=False,
                        convert_to_numpy=True
                    )
                    embeddings.append(batch_embeddings)
                
                return np.vstack(embeddings)
            else:
                return self.model.encode(texts, show_progress_bar=False)
        else:
            # Fallback to a simple Bag-of-Words approach
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=5000)
            return vectorizer.fit_transform(texts).toarray()
    
    def _compute_similarities(self, query_embedding: np.ndarray, chunk_embeddings: np.ndarray) -> np.ndarray:
        """
        Compute similarities between query and chunk embeddings.
        
        Args:
            query_embedding: Embedding of the query
            chunk_embeddings: Embeddings of the chunks
            
        Returns:
            similarities: Array of similarity scores
        """
        if self.similarity_metric == "cosine":
            # Normalize the embeddings for cosine similarity
            query_norm = np.linalg.norm(query_embedding)
            if query_norm > 0:
                query_embedding = query_embedding / query_norm
            
            # Compute cosine similarity efficiently
            return np.dot(chunk_embeddings, query_embedding)
        elif self.similarity_metric == "dot":
            # Simple dot product
            return np.dot(chunk_embeddings, query_embedding)
        elif self.similarity_metric == "euclidean":
            # Negative Euclidean distance (higher is more similar)
            return -np.sqrt(np.sum((chunk_embeddings - query_embedding) ** 2, axis=1))
        else:
            # Default to cosine
            return np.dot(chunk_embeddings, query_embedding)
    
    def index_chunks(self, chunks: List[Chunk]) -> None:
        """
        Index chunks for future retrieval.
        
        Args:
            chunks: Chunks to index
        """
        if not chunks:
            return
        
        # Add new chunks
        for chunk in chunks:
            # Skip if chunk is already indexed
            if chunk.chunk_id in self.chunk_ids_to_index:
                continue
            
            self.chunks.append(chunk)
            self.chunk_ids_to_index[chunk.chunk_id] = len(self.chunks) - 1
        
        # Get embeddings for all chunks
        chunk_texts = [chunk.content for chunk in self.chunks]
        self.chunk_embeddings = self._get_embeddings(chunk_texts)
        
        # Apply dimensionality reduction if needed for memory efficiency
        if (self.max_index_size is not None and 
            len(self.chunks) > self.max_index_size and 
            self.model is not None):
            
            # Keep only the most recent chunks
            self.chunks = self.chunks[-self.max_index_size:]
            
            # Update the index mapping
            self.chunk_ids_to_index = {
                chunk.chunk_id: i for i, chunk in enumerate(self.chunks)
            }
            
            # Recalculate embeddings for the pruned set
            chunk_texts = [chunk.content for chunk in self.chunks]
            self.chunk_embeddings = self._get_embeddings(chunk_texts)
        
        # Normalize embeddings for cosine similarity
        if self.similarity_metric == "cosine" and self.chunk_embeddings is not None:
            # Compute norms of each embedding vector
            norms = np.linalg.norm(self.chunk_embeddings, axis=1, keepdims=True)
            
            # Avoid division by zero - normalize only where norm > 0
            non_zero_norms = norms > 0
            if np.any(non_zero_norms):
                # Directly normalize by dividing by norms (with keepdims=True, broadcasting works correctly)
                self.chunk_embeddings = np.where(
                    non_zero_norms, 
                    self.chunk_embeddings / norms, 
                    self.chunk_embeddings
                )
        
        logger.info("Indexed %d chunks (total: %d)", len(chunks), len(self.chunks))
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Chunk]:
        """
        Retrieve chunks relevant to a query.
        
        Args:
            query: Query to retrieve chunks for
            top_k: Number of chunks to retrieve (default: 5)
            
        Returns:
            chunks: List of retrieved chunks
        """
        if not self.chunks:
            logger.warning("No chunks indexed for retrieval")
            return []
        
        if not query:
            logger.warning("Empty query provided")
            return []
        
        # Default top_k
        top_k = top_k or 5
        
        # Get query embedding
        query_embedding = self._get_embeddings([query])[0]
        
        # Compute similarities
        similarities = self._compute_similarities(query_embedding, self.chunk_embeddings)
        
        # Get indices of top-k most similar chunks
        if top_k >= len(similarities):
            top_indices = list(range(len(similarities)))
            top_indices.sort(key=lambda i: similarities[i], reverse=True)
        else:
            # More efficient partial sort for large indices
            top_indices = heapq.nlargest(top_k, range(len(similarities)), key=lambda i: similarities[i])
        
        # Get the corresponding chunks
        retrieved_chunks = [self.chunks[i] for i in top_indices]
        
        logger.info("Retrieved %d chunks for query", len(retrieved_chunks))
        return retrieved_chunks
    
    def clear(self) -> None:
        """Clear all indexed chunks."""
        self.chunks = []
        self.chunk_embeddings = None
        self.chunk_ids_to_index = {}
        logger.info("Cleared chunk index")
