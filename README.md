# efficient-context

A Python library for optimizing LLM context handling in CPU-constrained environments.

## Overview

`efficient-context` addresses the challenge of working with large language models (LLMs) on CPU-only and memory-limited systems by providing efficient context management strategies. The library focuses on:

- **Context Compression**: Reduce memory requirements while preserving information quality
- **Semantic Chunking**: Go beyond token-based approaches for more effective context management
- **Retrieval Optimization**: Minimize context size through intelligent retrieval strategies
- **Memory Management**: Handle large contexts on limited hardware resources

## Installation

```bash
pip install efficient-context
```

## Quick Start

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
optimized_context = context_manager.generate_context(query="Tell me about the climate impact of renewable energy")

# Use the optimized context with your LLM
response = your_llm_model.generate(prompt=prompt, context=optimized_context)
```

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

## Maintainer

This project is maintained by [Biswanath Roul](https://github.com/biswanathroul)

## License

MIT