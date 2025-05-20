"""
Tests for the core functionality of efficient-context.
"""

import unittest
from efficient_context import ContextManager
from efficient_context.compression import SemanticDeduplicator
from efficient_context.chunking import SemanticChunker, Chunk
from efficient_context.retrieval import CPUOptimizedRetriever
from efficient_context.memory import MemoryManager

class TestEfficientContext(unittest.TestCase):
    """Test cases for efficient-context functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.sample_text = """
        Renewable energy is derived from natural sources that are replenished at a higher rate than they are consumed.
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
        together with further electrification, which has several benefits: electricity can be converted to heat, 
        can be converted into mechanical energy with high efficiency, and is clean at the point of consumption.
        """
    
    def test_semantic_deduplicator(self):
        """Test the semantic deduplicator functionality."""
        compressor = SemanticDeduplicator(threshold=0.9)
        compressed = compressor.compress(self.sample_text)
        
        # Test that compression reduces size
        self.assertLess(len(compressed), len(self.sample_text))
        
        # Test that key content is preserved
        self.assertIn("Renewable energy", compressed)
    
    def test_semantic_chunker(self):
        """Test the semantic chunker functionality."""
        chunker = SemanticChunker(chunk_size=100, chunk_overlap=10)
        chunks = chunker.chunk(self.sample_text, document_id="test-doc")
        
        # Test that chunks were created
        self.assertGreater(len(chunks), 0)
        
        # Test that each chunk has content and metadata
        for chunk in chunks:
            self.assertIsInstance(chunk, Chunk)
            self.assertTrue(chunk.content)
            self.assertEqual(chunk.document_id, "test-doc")
    
    def test_cpu_optimized_retriever(self):
        """Test the CPU-optimized retriever functionality."""
        retriever = CPUOptimizedRetriever(embedding_model="lightweight")
        
        # Create test chunks
        chunks = [
            Chunk(content="Renewable energy is a sustainable energy source.", chunk_id="1"),
            Chunk(content="Climate change is a global challenge.", chunk_id="2"),
            Chunk(content="Fossil fuels contribute to greenhouse gas emissions.", chunk_id="3")
        ]
        
        # Index chunks
        retriever.index_chunks(chunks)
        
        # Test retrieval
        query = "What are the environmental impacts of energy sources?"
        results = retriever.retrieve(query, top_k=2)
        
        # Should return some results
        self.assertEqual(len(results), 2)
        
        # Clear index
        retriever.clear()
        self.assertEqual(len(retriever.chunks), 0)
    
    def test_context_manager_integration(self):
        """Test full integration of all components."""
        # Initialize context manager
        context_manager = ContextManager(
            compressor=SemanticDeduplicator(threshold=0.85),
            chunker=SemanticChunker(chunk_size=100),
            retriever=CPUOptimizedRetriever(embedding_model="lightweight"),
            memory_manager=MemoryManager()
        )
        
        # Add document
        doc_id = context_manager.add_document(self.sample_text)
        
        # Test document was added
        self.assertIn(doc_id, context_manager.documents)
        
        # Test context generation
        query = "Tell me about renewable energy in rural areas"
        context = context_manager.generate_context(query)
        
        # Should return some context
        self.assertTrue(context)
        
        # Clear context manager
        context_manager.clear()
        self.assertEqual(len(context_manager.documents), 0)
        self.assertEqual(len(context_manager.chunks), 0)

if __name__ == "__main__":
    unittest.main()
