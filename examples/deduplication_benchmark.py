#!/usr/bin/env python
"""
Specialized benchmark script for measuring the effectiveness of semantic deduplication
in the efficient-context library.
"""

import logging
import time
import argparse
import sys
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the library
try:
    from efficient_context import ContextManager
    from efficient_context.compression import SemanticDeduplicator
    from efficient_context.chunking import SemanticChunker
    from efficient_context.retrieval import CPUOptimizedRetriever
except ImportError as e:
    logger.error(f"Failed to import efficient_context: {e}")
    sys.exit(1)

def generate_repetitive_document() -> str:
    """
    Generate a document with deliberate semantic repetition.
    The document will contain sentences that mean the same thing
    expressed in different ways.
    """
    # Base paragraphs with distinct topics
    base_paragraphs = [
        # Climate change paragraph with repetitive content
        """
        Climate change is a significant and lasting alteration in the statistical distribution of weather 
        patterns over periods ranging from decades to millions of years. Global warming is the long-term 
        heating of Earth's climate system observed since the pre-industrial period due to human activities.
        The rise in global temperature is causing substantial changes in our environment and ecosystems.
        The warming of the planet is leading to significant transformations in weather patterns worldwide.
        Human activities are causing Earth's temperature to increase, resulting in climate modifications.
        The climate crisis is fundamentally altering the Earth's atmosphere and affecting all living things.
        """,
        
        # Renewable energy paragraph with repetitive content
        """
        Renewable energy comes from sources that are naturally replenishing but flow-limited.
        Clean energy is derived from natural processes that are constantly replenished.
        Sustainable power is generated from resources that won't deplete over time.
        Green energy utilizes sources that don't produce pollution when generating power.
        Alternative energy refers to sources that are an alternative to fossil fuel.
        Eco-friendly power generation relies on inexhaustible natural resources.
        """,
        
        # Technology paragraph with repetitive content
        """
        Artificial intelligence is revolutionizing how we interact with technology.
        Machine learning is transforming the way computers process information.
        AI is fundamentally changing our relationship with digital systems.
        Smart algorithms are reshaping our technological landscape dramatically.
        Computational intelligence is altering how machines solve complex problems.
        Neural networks are revolutionizing the capabilities of modern computers.
        """
    ]
    
    # Repeat the paragraphs to create a longer document
    document = "\n\n".join(base_paragraphs * 3)
    return document

def generate_mixed_document() -> str:
    """
    Generate a document with a mix of repetitive and unique content.
    """
    repetitive = generate_repetitive_document()
    
    unique = """
    Energy efficiency is the goal to reduce the amount of energy required to provide products and services.
    For example, insulating a home allows a building to use less heating and cooling energy to achieve and
    maintain a comfortable temperature. Installing LED bulbs, fluorescent lighting, or natural skylights reduces
    the amount of energy required to attain the same level of illumination compared with using traditional
    incandescent light bulbs. Improvements in energy efficiency are generally achieved by adopting a more
    efficient technology or production process or by application of commonly accepted methods to reduce energy
    losses.
    
    Biodiversity is the variety and variability of life on Earth. It is typically a measure of variation at the
    genetic, species, and ecosystem level. Terrestrial biodiversity is usually greater near the equator, which is
    the result of the warm climate and high primary productivity. Biodiversity is not distributed evenly on Earth,
    and is richer in the tropics. These tropical forest ecosystems cover less than 10% of earth's surface, and
    contain about 90% of the world's species. Marine biodiversity is usually highest along coasts in the Western
    Pacific, where sea surface temperature is highest, and in the mid-latitudinal band in all oceans.
    """
    
    return repetitive + "\n\n" + unique

def generate_repetitive_document() -> str:
    """
    Generate a document with deliberate semantic repetition.
    The document will contain sentences that mean the same thing
    expressed in different ways.
    """
    # Base paragraphs with distinct topics
    base_paragraphs = [
        # Climate change paragraph with repetitive content
        """
        Climate change is a significant and lasting alteration in the statistical distribution of weather 
        patterns over periods ranging from decades to millions of years. Global warming is the long-term 
        heating of Earth's climate system observed since the pre-industrial period due to human activities.
        The rise in global temperature is causing substantial changes in our environment and ecosystems.
        The warming of the planet is leading to significant transformations in weather patterns worldwide.
        Human activities are causing Earth's temperature to increase, resulting in climate modifications.
        The climate crisis is fundamentally altering the Earth's atmosphere and affecting all living things.
        """,
        
        # Renewable energy paragraph with repetitive content
        """
        Renewable energy comes from sources that are naturally replenishing but flow-limited.
        Clean energy is derived from natural processes that are constantly replenished.
        Sustainable power is generated from resources that won't deplete over time.
        Green energy utilizes sources that don't produce pollution when generating power.
        Alternative energy refers to sources that are an alternative to fossil fuel.
        Eco-friendly power generation relies on inexhaustible natural resources.
        """,
        
        # Technology paragraph with repetitive content
        """
        Artificial intelligence is revolutionizing how we interact with technology.
        Machine learning is transforming the way computers process information.
        AI is fundamentally changing our relationship with digital systems.
        Smart algorithms are reshaping our technological landscape dramatically.
        Computational intelligence is altering how machines solve complex problems.
        Neural networks are revolutionizing the capabilities of modern computers.
        """
    ]
    
    # Repeat the paragraphs to create a longer document
    document = "\n\n".join(base_paragraphs * 3)
    return document

def generate_mixed_document() -> str:
    """
    Generate a document with a mix of repetitive and unique content.
    """
    repetitive = generate_repetitive_document()
    
    unique = """
    Energy efficiency is the goal to reduce the amount of energy required to provide products and services.
    For example, insulating a home allows a building to use less heating and cooling energy to achieve and
    maintain a comfortable temperature. Installing LED bulbs, fluorescent lighting, or natural skylights reduces
    the amount of energy required to attain the same level of illumination compared with using traditional
    incandescent light bulbs. Improvements in energy efficiency are generally achieved by adopting a more
    efficient technology or production process or by application of commonly accepted methods to reduce energy
    losses.
    
    Biodiversity is the variety and variability of life on Earth. It is typically a measure of variation at the
    genetic, species, and ecosystem level. Terrestrial biodiversity is usually greater near the equator, which is
    the result of the warm climate and high primary productivity. Biodiversity is not distributed evenly on Earth,
    and is richer in the tropics. These tropical forest ecosystems cover less than 10% of earth's surface, and
    contain about 90% of the world's species. Marine biodiversity is usually highest along coasts in the Western
    Pacific, where sea surface temperature is highest, and in the mid-latitudinal band in all oceans.
    """
    
    return repetitive + "\n\n" + unique

def run_deduplication_benchmark() -> None:
    """
    Run a benchmark specifically testing the semantic deduplication capabilities.
    """
    logger.info("Starting deduplication benchmark")
    
    # Initialize context manager with various thresholds
    thresholds = [0.7, 0.8, 0.85, 0.9, 0.95]
    results = []
    
    # Create documents
    repetitive_doc = generate_repetitive_document()
    mixed_doc = generate_mixed_document()
    
    logger.info(f"Repetitive document size: {len(repetitive_doc.split())} words")
    logger.info(f"Mixed document size: {len(mixed_doc.split())} words")
    
    for threshold in thresholds:
        logger.info(f"\nTesting with threshold: {threshold}")
        
        # Create a fresh context manager with the current threshold
        context_manager = ContextManager(
            compressor=SemanticDeduplicator(threshold=threshold),
            chunker=SemanticChunker(chunk_size=256),
            retriever=CPUOptimizedRetriever(embedding_model="lightweight")
        )
        
        # Test with repetitive document
        logger.info("Processing repetitive document...")
        start_time = time.time()
        doc_id = context_manager.add_document(repetitive_doc)
        processing_time = time.time() - start_time
        
        # Generate context with a relevant query to see compression in action
        query = "Tell me about climate change and renewable energy"
        start_time = time.time()
        context = context_manager.generate_context(query)
        query_time = time.time() - start_time
        
        # Record result
        result = {
            "threshold": threshold,
            "document_type": "repetitive",
            "original_size": len(repetitive_doc.split()),
            "context_size": len(context.split()),
            "processing_time": processing_time,
            "query_time": query_time,
            "chunks": len(context_manager.chunks)
        }
        results.append(result)
        logger.info(f"  - Original size: {result['original_size']} words")
        logger.info(f"  - Context size: {result['context_size']} words")
        logger.info(f"  - Compression ratio: {result['context_size'] / result['original_size']:.2f}")
        logger.info(f"  - Processing time: {result['processing_time']:.4f} seconds")
        logger.info(f"  - Query time: {result['query_time']:.4f} seconds")
        
        # Reset the context manager
        context_manager = ContextManager(
            compressor=SemanticDeduplicator(threshold=threshold),
            chunker=SemanticChunker(chunk_size=256),
            retriever=CPUOptimizedRetriever(embedding_model="lightweight")
        )
        
        # Test with mixed document
        logger.info("Processing mixed document...")
        start_time = time.time()
        doc_id = context_manager.add_document(mixed_doc)
        processing_time = time.time() - start_time
        
        # Generate context with a relevant query
        query = "Tell me about climate change and biodiversity"
        start_time = time.time()
        context = context_manager.generate_context(query)
        query_time = time.time() - start_time
        
        # Record result
        result = {
            "threshold": threshold,
            "document_type": "mixed",
            "original_size": len(mixed_doc.split()),
            "context_size": len(context.split()),
            "processing_time": processing_time,
            "query_time": query_time,
            "chunks": len(context_manager.chunks)
        }
        results.append(result)
        logger.info(f"  - Original size: {result['original_size']} words")
        logger.info(f"  - Context size: {result['context_size']} words")
        logger.info(f"  - Compression ratio: {result['context_size'] / result['original_size']:.2f}")
        logger.info(f"  - Processing time: {result['processing_time']:.4f} seconds")
        logger.info(f"  - Query time: {result['query_time']:.4f} seconds")
    
    # Print summary
    logger.info("\nDeduplication Benchmark Summary:")
    logger.info("-----------------------------------")
    
    logger.info("\nRepetitive Document Results:")
    for result in [r for r in results if r["document_type"] == "repetitive"]:
        logger.info(f"Threshold {result['threshold']}: {result['context_size'] / result['original_size']:.2f} compression ratio, {result['processing_time']:.4f}s processing time")
    
    logger.info("\nMixed Document Results:")
    for result in [r for r in results if r["document_type"] == "mixed"]:
        logger.info(f"Threshold {result['threshold']}: {result['context_size'] / result['original_size']:.2f} compression ratio, {result['processing_time']:.4f}s processing time")

def main():
    """Main function for the deduplication benchmark script."""
    parser = argparse.ArgumentParser(description="Benchmark efficient-context's semantic deduplication")
    
    args = parser.parse_args()
    run_deduplication_benchmark()

if __name__ == "__main__":
    main()
