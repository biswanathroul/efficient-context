# efficient-context Documentation

## Overview

`efficient-context` is a Python library designed to optimize the handling of context for Large Language Models (LLMs) in CPU-constrained environments. It addresses the challenges of using LLMs with limited computational resources by providing efficient context management strategies.

## Key Features

1. **Context Compression**: Reduce memory requirements while preserving information quality
2. **Semantic Chunking**: Go beyond token-based approaches for more effective context management
3. **Retrieval Optimization**: Minimize context size through intelligent retrieval strategies
4. **Memory Management**: Handle large contexts on limited hardware resources

## Installation

```bash
pip install efficient-context
```

## Core Components

### ContextManager

The central class that orchestrates all components of the library.

```python
from efficient_context import ContextManager

# Initialize with default settings
context_manager = ContextManager()

# Add documents
context_manager.add_document("This is a sample document about renewable energy...")
context_manager.add_documents([doc1, doc2, doc3])  # Add multiple documents

# Generate context for a query
optimized_context = context_manager.generate_context(query="Tell me about renewable energy")
```

### Context Compression

The compression module reduces the size of content while preserving key information.

```python
from efficient_context.compression import SemanticDeduplicator

# Initialize with custom settings
compressor = SemanticDeduplicator(
    threshold=0.85,  # Similarity threshold for deduplication
    embedding_model="lightweight",  # Use a lightweight embedding model
    min_sentence_length=10,  # Minimum length of sentences to consider
    importance_weight=0.3  # Weight given to sentence importance vs. deduplication
)

# Compress content
compressed_content = compressor.compress(
    content="Your large text content here...",
    target_size=1000  # Optional target size in tokens
)
```

### Semantic Chunking

The chunking module divides content into semantically coherent chunks.

```python
from efficient_context.chunking import SemanticChunker

# Initialize with custom settings
chunker = SemanticChunker(
    chunk_size=512,  # Target size for chunks in tokens
    chunk_overlap=50,  # Number of tokens to overlap between chunks
    respect_paragraphs=True,  # Avoid breaking paragraphs across chunks
    min_chunk_size=100,  # Minimum chunk size in tokens
    max_chunk_size=1024  # Maximum chunk size in tokens
)

# Chunk content
chunks = chunker.chunk(
    content="Your large text content here...",
    document_id="doc-1",  # Optional document ID
    metadata={"source": "example", "author": "John Doe"}  # Optional metadata
)
```

### Retrieval Optimization

The retrieval module finds the most relevant chunks for a query.

```python
from efficient_context.retrieval import CPUOptimizedRetriever

# Initialize with custom settings
retriever = CPUOptimizedRetriever(
    embedding_model="lightweight",  # Use a lightweight embedding model
    similarity_metric="cosine",  # Metric for comparing embeddings
    use_batching=True,  # Batch embedding operations
    batch_size=32,  # Size of batches for embedding
    max_index_size=5000  # Maximum number of chunks to keep in the index
)

# Index chunks
retriever.index_chunks(chunks)

# Retrieve relevant chunks
relevant_chunks = retriever.retrieve(
    query="Your query here...",
    top_k=5  # Number of chunks to retrieve
)
```

### Memory Management

The memory module helps optimize memory usage during operations.

```python
from efficient_context.memory import MemoryManager

# Initialize with custom settings
memory_manager = MemoryManager(
    target_usage_percent=80.0,  # Target memory usage percentage
    aggressive_cleanup=False,  # Whether to perform aggressive garbage collection
    memory_monitor_interval=None  # Interval for memory monitoring in seconds
)

# Use context manager for memory-intensive operations
with memory_manager.optimize_memory():
    # Run memory-intensive operations here
    results = process_large_documents(documents)

# Get memory usage statistics
memory_stats = memory_manager.get_memory_usage()
print(f"Process memory: {memory_stats['process_rss_bytes'] / (1024*1024):.2f} MB")
```

## Advanced Usage

### Customizing the Context Manager

```python
from efficient_context import ContextManager
from efficient_context.compression import SemanticDeduplicator
from efficient_context.chunking import SemanticChunker
from efficient_context.retrieval import CPUOptimizedRetriever
from efficient_context.memory import MemoryManager

# Initialize a fully customized context manager
context_manager = ContextManager(
    compressor=SemanticDeduplicator(threshold=0.85),
    chunker=SemanticChunker(chunk_size=256, chunk_overlap=50),
    retriever=CPUOptimizedRetriever(embedding_model="lightweight"),
    memory_manager=MemoryManager(target_usage_percent=80.0),
    max_context_size=4096
)
```

### Integration with LLMs

```python
from efficient_context import ContextManager
from your_llm_library import LLM  # Replace with your actual LLM library

# Initialize components
context_manager = ContextManager()
llm = LLM(model="lightweight-model")

# Process documents
context_manager.add_documents(documents)

# For each query
query = "Tell me about renewable energy"
optimized_context = context_manager.generate_context(query=query)

# Use context with the LLM
response = llm.generate(
    prompt=query,
    context=optimized_context,
    max_tokens=512
)
```

## Performance Considerations

- **Memory Usage**: The library is designed to be memory-efficient, but be aware that embedding models may still require significant memory.
- **CPU Performance**: Choose the appropriate embedding model based on your CPU capabilities. The `lightweight` option is recommended for constrained environments.
- **Batch Size**: Adjust the `batch_size` parameter in retrieval to balance between memory usage and processing speed.
- **Context Size**: Setting appropriate `max_context_size` can significantly impact performance, especially when working with limited resources.

## Extending the Library

You can create custom implementations of the base classes to adapt the library to your specific needs:

```python
from efficient_context.compression.base import BaseCompressor

class MyCustomCompressor(BaseCompressor):
    def __init__(self, custom_param=None):
        self.custom_param = custom_param
    
    def compress(self, content, target_size=None):
        # Your custom compression logic here
        return compressed_content
```

## Troubleshooting

**High Memory Usage**
- Reduce `batch_size` in the retriever
- Use a more lightweight embedding model
- Decrease `max_index_size` to limit the number of chunks stored in memory

**Slow Processing**
- Increase `batch_size` (balancing with memory constraints)
- Increase `threshold` in the SemanticDeduplicator to be more aggressive with deduplication
- Reduce `chunk_overlap` to minimize redundant processing

## Example Applications

- **Chatbots on Edge Devices**: Enable context-aware conversations on devices with limited resources
- **Document QA Systems**: Create efficient question-answering systems for large document collections
- **Embedded AI Applications**: Incorporate context-aware LLM capabilities in embedded systems
- **Mobile Applications**: Provide sophisticated LLM features in mobile apps with limited resources
