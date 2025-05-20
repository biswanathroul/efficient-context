#!/usr/bin/env python
"""
Simple benchmark for efficient-context's semantic deduplication.
"""

import logging
import time
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Simple deduplication benchmark starting")

# Import the library
try:
    from efficient_context import ContextManager
    from efficient_context.compression import SemanticDeduplicator
    from efficient_context.chunking import SemanticChunker
    from efficient_context.retrieval import CPUOptimizedRetriever
    logger.info("Successfully imported efficient_context")
except ImportError as e:
    logger.error(f"Failed to import efficient_context: {e}")
    sys.exit(1)

def create_repetitive_document():
    """Create a document with deliberate repetition"""
    # Base paragraphs with repetitive content
    climate_paragraph = """
    Climate change is a significant alteration in weather patterns over extended periods.
    Global warming is the long-term heating of Earth's climate system due to human activities.
    Rising global temperatures are causing substantial changes in our environment and ecosystems.
    The warming of the planet is leading to significant transformations in weather patterns.
    Human activities are causing Earth's temperature to increase, resulting in climate changes.
    """
    
    energy_paragraph = """
    Renewable energy comes from sources that are naturally replenishing but flow-limited.
    Clean energy is derived from natural processes that are constantly replenished.
    Sustainable power is generated from resources that won't deplete over time.
    Green energy utilizes sources that don't produce pollution when generating power.
    Alternative energy refers to sources that are an alternative to fossil fuel.
    """
    
    # Repeat the paragraphs to create a more repetitive document
    document = (climate_paragraph + energy_paragraph) * 3
    return document

def main():
    """Run the benchmark"""
    # Create the test document
    document = create_repetitive_document()
    logger.info(f"Document size: {len(document.split())} words")
    
    # Test with different thresholds
    thresholds = [0.7, 0.8, 0.85, 0.9, 0.95]
    
    for threshold in thresholds:
        logger.info(f"\nTesting with threshold: {threshold}")
        
        # Create a context manager with the current threshold
        context_manager = ContextManager(
            compressor=SemanticDeduplicator(threshold=threshold),
            chunker=SemanticChunker(chunk_size=100),
            retriever=CPUOptimizedRetriever(embedding_model="lightweight")
        )
        
        # Process the document
        start_time = time.time()
        doc_id = context_manager.add_document(document)
        processing_time = time.time() - start_time
        
        # Generate context with a query
        query = "Tell me about climate change and renewable energy"
        start_time = time.time()
        context = context_manager.generate_context(query)
        query_time = time.time() - start_time
        
        # Report results
        original_size = len(document.split())
        context_size = len(context.split())
        compression_ratio = context_size / original_size if original_size > 0 else 1.0
        
        logger.info(f"Results for threshold {threshold}:")
        logger.info(f"  - Original size: {original_size} words")
        logger.info(f"  - Context size: {context_size} words")
        logger.info(f"  - Compression ratio: {compression_ratio:.2f}")
        logger.info(f"  - Processing time: {processing_time:.4f} seconds")
        logger.info(f"  - Query time: {query_time:.4f} seconds")

if __name__ == "__main__":
    main()
