#!/usr/bin/env python
"""
Advanced test for efficient-context's deduplication capabilities
"""

import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the library
from efficient_context import ContextManager
from efficient_context.compression import SemanticDeduplicator
from efficient_context.chunking import SemanticChunker
from efficient_context.retrieval import CPUOptimizedRetriever

def create_repetitive_document():
    """Create a document with highly repetitive semantic content"""
    
    # Create repetitive paragraphs with the same semantic meaning expressed differently
    paragraphs = []
    
    # Climate change variations
    climate_variations = [
        "Climate change is a significant alteration in global weather patterns over extended periods.",
        "Global warming refers to the long-term increase in Earth's average temperature.",
        "The climate crisis is causing significant shifts in temperature and precipitation patterns worldwide.",
        "Rising global temperatures lead to fundamental changes in our planet's climate systems.",
        "Human-induced warming of the Earth's atmosphere is resulting in climate destabilization."
    ]
    paragraphs.extend(climate_variations)
    
    # Renewable energy variations
    energy_variations = [
        "Renewable energy comes from natural sources that are constantly replenished.",
        "Clean energy technologies harness power from sustainable, non-depleting resources.",
        "Green power is generated from environmentally friendly, renewable sources.",
        "Sustainable energy is derived from resources that don't run out over time.",
        "Alternative energy refers to power sources that are alternatives to fossil fuels."
    ]
    paragraphs.extend(energy_variations)
    
    # Add some unique content as well
    unique_content = [
        "Machine learning algorithms require significant computational resources to train effectively.",
        "Biodiversity loss is accelerating at an unprecedented rate due to human activities.",
        "Quantum computing may revolutionize cryptography and computational chemistry."
    ]
    paragraphs.extend(unique_content)
    
    # Repeat the document to make it longer and more repetitive
    document = "\n\n".join(paragraphs * 3)  # Repeat 3 times
    return document

def run_deduplication_test():
    """Test the semantic deduplication capabilities"""
    logger.info("Running semantic deduplication test")
    
    # Create a highly repetitive document
    document = create_repetitive_document()
    logger.info(f"Document size: {len(document.split())} words")
    
    # Test with different threshold values
    thresholds = [0.7, 0.8, 0.85, 0.9, 0.95]
    
    for threshold in thresholds:
        logger.info(f"\nTesting threshold: {threshold}")
        
        # Create context manager with current threshold
        cm = ContextManager(
            compressor=SemanticDeduplicator(threshold=threshold),
            chunker=SemanticChunker(chunk_size=200),
            retriever=CPUOptimizedRetriever(embedding_model="lightweight")
        )
        
        # Add document and measure processing time
        start = time.time()
        doc_id = cm.add_document(document)
        processing_time = time.time() - start
        
        # Generate context for a relevant query
        query = "Explain the relationship between climate change and renewable energy"
        start = time.time()
        context = cm.generate_context(query)
        query_time = time.time() - start
        
        # Calculate metrics
        original_size = len(document.split())
        context_size = len(context.split())
        compression_ratio = context_size / original_size
        
        # Report results
        logger.info(f"Results for threshold {threshold}:")
        logger.info(f"  - Original document: {original_size} words")
        logger.info(f"  - Context generated: {context_size} words")
        logger.info(f"  - Compression ratio: {compression_ratio:.2f}")
        logger.info(f"  - Chunks created: {len(cm.chunks)}")
        logger.info(f"  - Processing time: {processing_time:.4f} seconds")
        logger.info(f"  - Query time: {query_time:.4f} seconds")
        
        # Print a preview of the context
        logger.info(f"  - Context preview: {context[:150]}...")

if __name__ == "__main__":
    try:
        print("Starting deduplication evaluation...")
        run_deduplication_test()
        print("Evaluation completed successfully")
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
