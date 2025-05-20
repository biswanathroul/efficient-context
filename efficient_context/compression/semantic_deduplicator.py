"""
Semantic deduplication for compressing context content.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from efficient_context.compression.base import BaseCompressor
from efficient_context.utils.text import split_into_sentences, get_sentence_importance

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticDeduplicator(BaseCompressor):
    """
    Compressor that removes semantically duplicate or redundant content.
    
    This compressor identifies and removes sentences that are semantically
    similar to others in the content, keeping only the most representative ones.
    It's designed to be CPU-friendly and memory-efficient.
    """
    
    def __init__(
        self,
        threshold: float = 0.85,
        embedding_model: str = "lightweight",
        min_sentence_length: int = 10,
        importance_weight: float = 0.3,
    ):
        """
        Initialize the SemanticDeduplicator.
        
        Args:
            threshold: Similarity threshold for considering content duplicated (0.0 to 1.0)
            embedding_model: The model to use for generating embeddings
            min_sentence_length: Minimum length of sentences to consider
            importance_weight: Weight given to sentence importance vs. deduplication
        """
        self.threshold = threshold
        self.embedding_model = embedding_model
        self.min_sentence_length = min_sentence_length
        self.importance_weight = importance_weight
        
        # Initialize the embedding model
        self._init_embedding_model()
        
        logger.info("SemanticDeduplicator initialized with threshold: %.2f", threshold)
    
    def _init_embedding_model(self):
        """Initialize the embedding model based on the selected type."""
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
    
    def _get_embeddings(self, sentences: List[str]) -> np.ndarray:
        """
        Get embeddings for a list of sentences.
        
        Args:
            sentences: List of sentences to embed
            
        Returns:
            embeddings: Array of sentence embeddings
        """
        if not sentences:
            return np.array([])
            
        if self.model is not None:
            # Use the sentence transformer if available
            return self.model.encode(sentences, show_progress_bar=False)
        else:
            # Fallback to a simple Bag-of-Words approach
            # This is much less accurate but works without dependencies
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=5000)
            return vectorizer.fit_transform(sentences).toarray()
    
    def _compute_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Compute pairwise similarity between embeddings.
        
        Args:
            embeddings: Array of sentence embeddings
            
        Returns:
            similarity_matrix: Matrix of pairwise similarities
        """
        # Return empty array for empty input
        if embeddings.shape[0] == 0:
            return np.array([])
            
        # Compute cosine similarity
        return cosine_similarity(embeddings)
    
    def _deduplicate_sentences(
        self, 
        sentences: List[str], 
        importances: Optional[List[float]] = None
    ) -> List[int]:
        """
        Identify non-redundant sentence indices.
        
        Args:
            sentences: List of sentences to deduplicate
            importances: Optional list of importance scores
            
        Returns:
            kept_indices: Indices of sentences to keep
        """
        if not sentences:
            return []
            
        # Filter out sentences that are too short
        valid_indices = [i for i, s in enumerate(sentences) if len(s.split()) >= self.min_sentence_length]
        
        if not valid_indices:
            # If no sentences meet the min length, return all indices
            return list(range(len(sentences)))
            
        # Get embeddings for valid sentences
        valid_sentences = [sentences[i] for i in valid_indices]
        embeddings = self._get_embeddings(valid_sentences)
        
        # Compute pairwise similarity
        similarity_matrix = self._compute_similarity_matrix(embeddings)
        
        # Set diagonal to 0 to avoid self-similarity
        np.fill_diagonal(similarity_matrix, 0)
        
        # Determine which sentences to keep
        kept_indices = []
        remaining_indices = set(range(len(valid_indices)))
        
        # If importances are provided, start with most important sentences
        if importances is not None:
            valid_importances = [importances[i] for i in valid_indices]
            ordered_indices = [i for i, _ in sorted(
                enumerate(valid_importances), 
                key=lambda x: x[1], 
                reverse=True
            )]
        else:
            # Otherwise, use sentence length as a simple importance proxy
            ordered_indices = [i for i, _ in sorted(
                enumerate(valid_sentences), 
                key=lambda x: len(x[1].split()), 
                reverse=True
            )]
        
        # Process sentences in order of importance
        for idx in ordered_indices:
            if idx not in remaining_indices:
                continue
                
            # Keep this sentence
            kept_indices.append(valid_indices[idx])
            remaining_indices.remove(idx)
            
            # Remove similar sentences
            similar_indices = [
                i for i in remaining_indices 
                if similarity_matrix[idx, i] > self.threshold
            ]
            
            remaining_indices -= set(similar_indices)
            
            # Break if we've processed all indices
            if not remaining_indices:
                break
        
        # Add any remaining short sentences we skipped earlier
        short_indices = [i for i, s in enumerate(sentences) if len(s.split()) < self.min_sentence_length]
        kept_indices.extend(short_indices)
        
        # Sort to maintain original order
        return sorted(kept_indices)
    
    def compress(self, content: str, target_size: Optional[int] = None) -> str:
        """
        Compress content by removing semantic duplicates.
        
        Args:
            content: The content to compress
            target_size: Optional target size in tokens
            
        Returns:
            compressed_content: The compressed content
        """
        # Split content into sentences
        sentences = split_into_sentences(content)
        
        if not sentences:
            return content
            
        # Get sentence importance scores
        importances = get_sentence_importance(sentences)
        
        # Deduplicate sentences
        kept_indices = self._deduplicate_sentences(sentences, importances)
        
        # Combine kept sentences
        kept_sentences = [sentences[i] for i in kept_indices]
        compressed = " ".join(kept_sentences)
        
        # If we need to compress further to meet target size
        if target_size and len(compressed.split()) > target_size:
            # Calculate how many more sentences to remove
            current_size = len(compressed.split())
            reduction_needed = current_size - target_size
            
            # Sort sentences by importance (lowest first)
            sentence_priorities = [(i, importances[i]) for i in kept_indices]
            sorted_priorities = sorted(sentence_priorities, key=lambda x: x[1])
            
            # Remove least important sentences until we meet target size
            remove_count = 0
            tokens_removed = 0
            indices_to_remove = []
            
            for idx, _ in sorted_priorities:
                sentence_tokens = len(sentences[idx].split())
                tokens_removed += sentence_tokens
                remove_count += 1
                indices_to_remove.append(idx)
                
                if tokens_removed >= reduction_needed:
                    break
            
            # Remove the low-importance sentences
            final_indices = [i for i in kept_indices if i not in indices_to_remove]
            
            # Recombine
            compressed = " ".join(sentences[i] for i in sorted(final_indices))
        
        # Log compression stats
        original_tokens = len(content.split())
        compressed_tokens = len(compressed.split())
        reduction = (1 - compressed_tokens / original_tokens) * 100 if original_tokens > 0 else 0
        
        logger.info(
            "Compressed from %d to %d tokens (%.1f%% reduction)",
            original_tokens, compressed_tokens, reduction
        )
        
        return compressed
