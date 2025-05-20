---
library_name: efficient-context
language: python
tags:
  - context-optimization
  - llm
  - cpu-optimization
  - resource-constrained
  - memory-management
license: mit
datasets:
  - None
---

<!-- filepath: /Users/biswanath2.roul/Desktop/biswanath/office/poc/pypi/190525/efficient-context/model_card.md -->
# efficient-context

A Python library for optimizing LLM context handling in CPU-constrained environments.

## Model / Library Description

`efficient-context` addresses the challenge of working with large language models (LLMs) on CPU-only and memory-limited systems by providing efficient context management strategies. The library focuses on making LLMs more usable when computational resources are limited.

## Intended Use

This library is designed for:
- Deploying LLMs in resource-constrained environments
- Optimizing context handling for edge devices
- Creating applications that need to run on standard hardware
- Reducing memory usage when working with large documents

## Features

### Context Compression
- Semantic deduplication to remove redundant information
- Importance-based pruning that keeps critical information
- Automatic summarization of less relevant sections

### Advanced Chunking
- Semantic chunking that preserves logical units
- Adaptive chunk sizing based on content complexity
- Chunk relationships mapping for coherent retrieval

### Retrieval Optimization
- Lightweight embedding models optimized for CPU
- Tiered retrieval strategies (local vs. remote)
- Query-aware context assembly

### Memory Management
- Progressive loading/unloading of context
- Streaming context processing
- Memory-aware caching strategies

## Installation

```bash
pip install efficient-context
```

## Usage

```python
from efficient_context import ContextManager
from efficient_context.compression import SemanticDeduplicator
from efficient_context.chunking import SemanticChunker
from efficient_context.retrieval import CPUOptimizedRetriever

# Initialize a context manager with custom strategies
context_manager = ContextManager(
    compressor=SemanticDeduplicator(threshold=0.85),
    chunker=SemanticChunker(chunk_size=256),
    retriever=CPUOptimizedRetriever(embedding_model="lightweight")
)

# Add documents to your context
context_manager.add_documents(documents)

# Generate optimized context for a query
optimized_context = context_manager.generate_context(
    query="Tell me about the climate impact of renewable energy"
)

# Use the optimized context with your LLM
response = your_llm_model.generate(prompt=prompt, context=optimized_context)
```

## Performance and Benchmarks

The library has demonstrated excellent performance in handling repetitive content:
- With a threshold of 0.7, it achieved a 57.5% reduction in token count
- Processing times: 0.13-0.84 seconds for a 426-word document
- Query time: 0.08-0.14 seconds

## Limitations

- Designed primarily for text data
- Performance depends on the quality of embedding models
- Semantic deduplication may occasionally remove content that appears similar but has subtle differences

## Maintainer

This project is maintained by [Biswanath Roul](https://github.com/biswanathroul)

## License

MIT
```
