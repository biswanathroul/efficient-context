"""
Text processing utilities for the efficient-context library.
"""

import re
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences.
    
    Args:
        text: Text to split
        
    Returns:
        sentences: List of sentences
    """
    # Simple but effective sentence splitting
    # This handles most common sentence endings while preserving common abbreviations
    text = text.replace('\n', ' ')
    
    # Try to use NLTK if available for better sentence splitting
    try:
        import nltk
        try:
            return nltk.sent_tokenize(text)
        except Exception as e:
            logger.warning(f"NLTK sentence tokenizer error: {e}. Using fallback.")
            return _simple_sentence_split(text)
    except ImportError:
        logger.warning("NLTK not available, using fallback sentence splitter")
        return _simple_sentence_split(text)

def _simple_sentence_split(text: str) -> List[str]:
    """Fallback sentence splitter without dependencies."""
    # This is a simplified version, not as accurate as NLTK but works without dependencies
    # Handle common abbreviations to avoid splitting them
    for abbr in ['Mr.', 'Mrs.', 'Dr.', 'vs.', 'e.g.', 'i.e.', 'etc.']:
        text = text.replace(abbr, abbr.replace('.', '<POINT>'))
    
    # Split on sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Restore abbreviations
    sentences = [s.replace('<POINT>', '.') for s in sentences]
    
    # Remove empty sentences
    return [s for s in sentences if s.strip()]

def get_sentence_importance(sentences: List[str]) -> List[float]:
    """
    Calculate importance scores for sentences based on heuristics.
    
    Args:
        sentences: List of sentences to score
        
    Returns:
        importances: List of importance scores (0.0 to 1.0)
    """
    # Simple heuristics for scoring sentence importance
    importances = []
    
    for sentence in sentences:
        score = 0.0
        words = sentence.split()
        
        # Longer sentences tend to be more informative (up to a point)
        length_score = min(len(words) / 20, 1.0)
        
        # Keywords suggest important content
        keyword_score = 0.0
        keywords = ['important', 'significant', 'key', 'critical', 'crucial', 
                   'essential', 'main', 'major', 'primary', 'central',
                   'result', 'conclusion', 'finding', 'discovered', 'shows']
        
        for word in words:
            if word.lower() in keywords:
                keyword_score += 0.2
        
        keyword_score = min(keyword_score, 0.6)  # Cap keyword importance
        
        # Presence of numbers often indicates factual content
        number_score = 0.0
        if re.search(r'\d', sentence):
            number_score = 0.2
        
        # Combine scores
        score = 0.5 * length_score + 0.3 * keyword_score + 0.2 * number_score
        
        # Cap at 1.0
        importances.append(min(score, 1.0))
    
    return importances

def calculate_text_overlap(text1: str, text2: str) -> float:
    """
    Calculate simple text overlap between two strings.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        overlap_ratio: Ratio of shared tokens (0.0 to 1.0)
    """
    # Convert to sets of tokens
    tokens1 = set(text1.lower().split())
    tokens2 = set(text2.lower().split())
    
    # Calculate overlap
    if not tokens1 or not tokens2:
        return 0.0
    
    overlap = tokens1.intersection(tokens2)
    return len(overlap) / min(len(tokens1), len(tokens2))
