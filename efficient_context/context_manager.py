"""
Core context management module for efficient-context library.
"""

from typing import List, Dict, Any, Optional, Union
import logging
from pydantic import BaseModel, Field

from efficient_context.compression.base import BaseCompressor
from efficient_context.chunking.base import BaseChunker
from efficient_context.retrieval.base import BaseRetriever
from efficient_context.memory.memory_manager import MemoryManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Document(BaseModel):
    """A document to be processed by the context manager."""
    id: str = Field(..., description="Unique identifier for the document")
    content: str = Field(..., description="Text content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata for the document")

class ContextManager:
    """
    Main class for managing context efficiently for LLMs in CPU-constrained environments.
    
    This class orchestrates the compression, chunking, retrieval, and memory management
    components to optimize context handling for LLMs running on limited hardware.
    """
    
    def __init__(
        self,
        compressor: Optional[BaseCompressor] = None,
        chunker: Optional[BaseChunker] = None,
        retriever: Optional[BaseRetriever] = None,
        memory_manager: Optional[MemoryManager] = None,
        max_context_size: int = 4096,
    ):
        """
        Initialize the context manager with configurable components.
        
        Args:
            compressor: Component for compressing context content
            chunker: Component for chunking content
            retriever: Component for retrieving relevant chunks
            memory_manager: Component for managing memory usage
            max_context_size: Maximum size of context in tokens
        """
        from efficient_context.compression import SemanticDeduplicator
        from efficient_context.chunking import SemanticChunker
        from efficient_context.retrieval import CPUOptimizedRetriever
        from efficient_context.memory import MemoryManager
        
        self.compressor = compressor or SemanticDeduplicator()
        self.chunker = chunker or SemanticChunker()
        self.retriever = retriever or CPUOptimizedRetriever()
        self.memory_manager = memory_manager or MemoryManager()
        self.max_context_size = max_context_size
        
        self.documents = {}
        self.chunks = []
        
        logger.info("Context Manager initialized with max context size: %d", max_context_size)
    
    def add_document(self, document: Union[Document, Dict, str], document_id: Optional[str] = None) -> str:
        """
        Add a document to the context manager.
        
        Args:
            document: Document to add (can be a Document object, dict, or string content)
            document_id: Optional ID for the document (generated if not provided)
            
        Returns:
            document_id: ID of the added document
        """
        # Convert input to Document object
        if isinstance(document, str):
            if document_id is None:
                import uuid
                document_id = str(uuid.uuid4())
            doc = Document(id=document_id, content=document)
        elif isinstance(document, dict):
            if 'id' in document:
                document_id = document['id']
            elif document_id is None:
                import uuid
                document_id = str(uuid.uuid4())
            
            doc = Document(
                id=document_id,
                content=document.get('content', ''),
                metadata=document.get('metadata', {})
            )
        else:
            doc = document
            document_id = doc.id
        
        # Store the document
        self.documents[document_id] = doc
        
        # Process the document
        with self.memory_manager.optimize_memory():
            # Compress the document
            compressed_content = self.compressor.compress(doc.content)
            
            # Chunk the compressed content
            doc_chunks = self.chunker.chunk(compressed_content, metadata=doc.metadata, document_id=doc.id)
            
            # Index the chunks for retrieval
            self.retriever.index_chunks(doc_chunks)
            
            # Store the chunks
            self.chunks.extend(doc_chunks)
        
        logger.info("Added document with ID %s (%d chunks)", document_id, len(doc_chunks))
        return document_id
    
    def add_documents(self, documents: List[Union[Document, Dict, str]]) -> List[str]:
        """
        Add multiple documents to the context manager.
        
        Args:
            documents: List of documents to add
            
        Returns:
            document_ids: List of IDs of added documents
        """
        document_ids = []
        for doc in documents:
            doc_id = self.add_document(doc)
            document_ids.append(doc_id)
        
        return document_ids
    
    def generate_context(self, query: str, max_size: Optional[int] = None) -> str:
        """
        Generate optimized context for a given query.
        
        Args:
            query: The query for which to generate context
            max_size: Maximum size of the context (defaults to self.max_context_size)
            
        Returns:
            context: Optimized context for the query
        """
        max_size = max_size or self.max_context_size
        
        with self.memory_manager.optimize_memory():
            # Retrieve relevant chunks
            relevant_chunks = self.retriever.retrieve(query, top_k=max_size)
            
            # Combine chunks into a context
            context_parts = [chunk.content for chunk in relevant_chunks]
            
            # Final compression to ensure we're within size limits
            combined_context = "\n\n".join(context_parts)
            if len(combined_context.split()) > max_size:
                combined_context = self.compressor.compress(combined_context, target_size=max_size)
        
        logger.info("Generated context of size ~%d tokens for query", len(combined_context.split()))
        return combined_context
    
    def clear(self):
        """Clear all documents and chunks from the context manager."""
        self.documents = {}
        self.chunks = []
        self.retriever.clear()
        logger.info("Context manager cleared")
