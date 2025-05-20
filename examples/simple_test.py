#!/usr/bin/env python
"""
Basic test for efficient-context
"""

import os
import sys
import time

print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    print("Testing efficient-context library...")

    # Create a simple context manager
    from efficient_context import ContextManager
    from efficient_context.compression import SemanticDeduplicator
    from efficient_context.chunking import SemanticChunker
    from efficient_context.retrieval import CPUOptimizedRetriever
    
    print("Successfully imported efficient_context")
except Exception as e:
    print(f"Error importing efficient_context: {e}")
    sys.exit(1)

cm = ContextManager(
    compressor=SemanticDeduplicator(threshold=0.85),
    chunker=SemanticChunker(chunk_size=200),
    retriever=CPUOptimizedRetriever(embedding_model="lightweight")
)

# Add a document
doc = """
Renewable energy comes from sources that are naturally replenishing but flow-limited.
Clean energy is derived from natural processes that are constantly replenished.
Sustainable power is generated from resources that won't deplete over time.
Green energy utilizes sources that don't produce pollution when generating power.
Alternative energy refers to sources that are an alternative to fossil fuel.
Eco-friendly power generation relies on inexhaustible natural resources.

Climate change is a significant and lasting alteration in the statistical distribution 
of weather patterns over periods ranging from decades to millions of years. 
Global warming is the long-term heating of Earth's climate system observed since 
the pre-industrial period due to human activities.
"""

print(f"Document size: {len(doc.split())} words")

# Add the document
start = time.time()
doc_id = cm.add_document(doc)
processing_time = time.time() - start
print(f"Document processed in {processing_time:.4f} seconds")
print(f"Created {len(cm.chunks)} chunks")

# Generate context
query = "Tell me about renewable energy"
start = time.time()
context = cm.generate_context(query)
query_time = time.time() - start

# Print results
print(f"Query time: {query_time:.4f} seconds")
print(f"Context size: {len(context.split())} words")
print(f"Context: {context[:150]}...")

print("Test completed successfully")
