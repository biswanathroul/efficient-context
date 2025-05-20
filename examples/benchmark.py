"""
Benchmarking script for efficient-context performance.
"""

import logging
import time
import argparse
import random
import string
import psutil
import os
import gc
from typing import List, Dict, Any

from efficient_context import ContextManager
from efficient_context.compression import SemanticDeduplicator
from efficient_context.chunking import SemanticChunker
from efficient_context.retrieval import CPUOptimizedRetriever

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_random_text(words: int = 1000, paragraphs: int = 5) -> str:
    """
    Generate random text for benchmarking.
    
    Args:
        words: Number of words to generate
        paragraphs: Number of paragraphs to split the text into
        
    Returns:
        text: Generated random text
    """
    # List of common words for more realistic text
    common_words = [
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "I", 
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
        "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
        "renewable", "energy", "climate", "wind", "solar", "power", "change", "global",
        "sustainable", "resources", "efficiency", "emissions", "carbon", "technology"
    ]
    
    # Generate paragraphs
    result = []
    words_per_paragraph = words // paragraphs
    
    for i in range(paragraphs):
        paragraph_words = []
        for j in range(words_per_paragraph):
            # Occasionally add a random word for variety
            if random.random() < 0.1:
                word = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(3, 10)))
            else:
                word = random.choice(common_words)
                
            # Capitalize first word of sentence
            if j == 0 or paragraph_words[-1].endswith('.'):
                word = word.capitalize()
                
            # Add punctuation occasionally
            if j > 0 and j % random.randint(8, 15) == 0:
                word += '.'
            elif random.random() < 0.05:
                word += ','
                
            paragraph_words.append(word)
        
        # Ensure paragraph ends with period
        if not paragraph_words[-1].endswith('.'):
            paragraph_words[-1] += '.'
            
        result.append(' '.join(paragraph_words))
    
    return '\n\n'.join(result)

def get_memory_usage() -> Dict[str, Any]:
    """
    Get current memory usage.
    
    Returns:
        stats: Memory usage statistics
    """
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        "rss": memory_info.rss / (1024 * 1024),  # MB
        "vms": memory_info.vms / (1024 * 1024)   # MB
    }

def run_benchmark(
    num_documents: int = 10,
    words_per_document: int = 1000,
    num_queries: int = 5
) -> None:
    """
    Run a benchmark of efficient-context performance.
    
    Args:
        num_documents: Number of documents to process
        words_per_document: Number of words per document
        num_queries: Number of queries to run
    """
    logger.info(f"Starting benchmark with {num_documents} documents, {words_per_document} words each")
    
    # Initialize context manager
    context_manager = ContextManager(
        compressor=SemanticDeduplicator(threshold=0.85),
        chunker=SemanticChunker(chunk_size=256),
        retriever=CPUOptimizedRetriever(embedding_model="lightweight")
    )
    
    # Generate documents
    logger.info("Generating random documents...")
    documents = []
    for i in range(num_documents):
        content = generate_random_text(words=words_per_document, paragraphs=5)
        documents.append({
            "content": content,
            "metadata": {"id": f"doc-{i}", "source": "benchmark"}
        })
    
    # Measure document processing
    logger.info("Adding documents to context manager...")
    start_mem = get_memory_usage()
    start_time = time.time()
    
    document_ids = context_manager.add_documents(documents)
    
    end_time = time.time()
    end_mem = get_memory_usage()
    
    processing_time = end_time - start_time
    memory_increase = end_mem["rss"] - start_mem["rss"]
    
    logger.info(f"Document processing:")
    logger.info(f"  - Time: {processing_time:.2f} seconds")
    logger.info(f"  - Average per document: {processing_time / num_documents:.4f} seconds")
    logger.info(f"  - Memory usage increase: {memory_increase:.2f} MB")
    logger.info(f"  - Total chunks created: {len(context_manager.chunks)}")
    
    # Generate random queries
    logger.info("Generating context for queries...")
    queries = [
        f"Explain {random.choice(['renewable', 'sustainable', 'clean', 'alternative'])} energy",
        f"What are the {random.choice(['benefits', 'advantages', 'impacts', 'effects'])} of {random.choice(['solar', 'wind', 'hydro', 'geothermal'])} power?",
        f"How does {random.choice(['climate change', 'global warming', 'carbon emissions', 'greenhouse gases'])} affect the environment?",
        f"Discuss the {random.choice(['future', 'potential', 'limitations', 'challenges'])} of renewable energy",
        f"What is the {random.choice(['relationship', 'connection', 'link', 'correlation'])} between energy consumption and climate change?"
    ]
    
    # Ensure we have enough queries
    while len(queries) < num_queries:
        queries.append(f"Tell me about {random.choice(['energy', 'climate', 'sustainability', 'emissions'])}")
    
    # Select the requested number of queries
    selected_queries = random.sample(queries, min(num_queries, len(queries)))
    
    # Measure query processing
    total_query_time = 0
    total_query_tokens = 0
    
    for i, query in enumerate(selected_queries):
        # Clear some memory and cache before each query
        gc.collect()
        
        start_time = time.time()
        context = context_manager.generate_context(query)
        query_time = time.time() - start_time
        context_tokens = len(context.split())
        
        total_query_time += query_time
        total_query_tokens += context_tokens
        
        logger.info(f"Query {i+1}: '{query}'")
        logger.info(f"  - Time: {query_time:.4f} seconds")
        logger.info(f"  - Context size: {context_tokens} tokens")
    
    avg_query_time = total_query_time / num_queries
    avg_tokens = total_query_tokens / num_queries
    
    logger.info("\nBenchmark Summary:")
    logger.info(f"  - Documents processed: {num_documents} ({words_per_document} words each)")
    logger.info(f"  - Queries executed: {num_queries}")
    logger.info(f"  - Document processing time: {processing_time:.2f} seconds ({processing_time / num_documents:.4f}s per document)")
    logger.info(f"  - Average query time: {avg_query_time:.4f} seconds")
    logger.info(f"  - Average context size: {avg_tokens:.1f} tokens")
    logger.info(f"  - Final memory usage: {get_memory_usage()['rss']:.2f} MB")

def main():
    """Main function for the benchmark script."""
    parser = argparse.ArgumentParser(description="Benchmark efficient-context performance")
    parser.add_argument("--documents", type=int, default=10, help="Number of documents to process")
    parser.add_argument("--words", type=int, default=1000, help="Words per document")
    parser.add_argument("--queries", type=int, default=5, help="Number of queries to run")
    
    args = parser.parse_args()
    
    run_benchmark(
        num_documents=args.documents,
        words_per_document=args.words,
        num_queries=args.queries
    )

if __name__ == "__main__":
    main()
