"""
Simple test script for efficient-context library.
"""

import logging
from efficient_context import ContextManager
from efficient_context.compression import SemanticDeduplicator
from efficient_context.chunking import SemanticChunker
from efficient_context.retrieval import CPUOptimizedRetriever

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_functionality():
    """Test the basic functionality of the library."""
    print("\n=== Testing Basic Functionality ===")
    
    # Sample document - notice we've removed indentation and added more content
    document = """Renewable energy is derived from natural sources that are replenished at a higher rate than they are consumed.
Sunlight and wind, for example, are such sources that are constantly being replenished.
Renewable energy resources exist over wide geographical areas, in contrast to fossil fuels, 
which are concentrated in a limited number of countries.

Rapid deployment of renewable energy and energy efficiency technologies is resulting in significant 
energy security, climate change mitigation, and economic benefits.
In international public opinion surveys there is strong support for promoting renewable sources 
such as solar power and wind power.

While many renewable energy projects are large-scale, renewable technologies are also suited to rural 
and remote areas and developing countries, where energy is often crucial in human development.
As most of the renewable energy technologies provide electricity, renewable energy is often deployed 
together with further electrification, which has several benefits."""
    
    # Initialize context manager
    context_manager = ContextManager(
        compressor=SemanticDeduplicator(threshold=0.85),
        chunker=SemanticChunker(chunk_size=100),
        retriever=CPUOptimizedRetriever(embedding_model="lightweight")
    )
    
    # Add document
    print(f"Document length: {len(document.split())} words")
    doc_id = context_manager.add_document(document)
    print(f"Added document with ID: {doc_id}")
    print(f"Created {len(context_manager.chunks)} chunks")
    
    # Debug information about chunks
    if len(context_manager.chunks) > 0:
        print("\nChunk information:")
        for i, chunk in enumerate(context_manager.chunks):
            print(f"Chunk {i+1}: {len(chunk.content.split())} words")
            print(f"Content sample: {chunk.content[:50]}...")
    else:
        print("\nWARNING: No chunks were created. This is likely an issue with the chunker.")
        # Let's try direct chunking to debug
        print("\nTrying direct chunking:")
        chunks = context_manager.chunker.chunk(document, document_id=doc_id)
        print(f"Direct chunking created {len(chunks)} chunks")
        if len(chunks) > 0:
            print(f"Sample chunk content: {chunks[0].content[:50]}...")
    
    # Test query
    query = "Tell me about renewable energy sources"
    print(f"\nQuery: {query}")
    
    # Get context
    context = context_manager.generate_context(query)
    print(f"\nGenerated context ({len(context.split())} tokens):")
    print(context)
    
    print("\n=== Test completed successfully ===")

if __name__ == "__main__":
    test_basic_functionality()
