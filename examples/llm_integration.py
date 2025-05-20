"""
Example of integrating efficient-context with a lightweight LLM.
"""

import logging
import time
from typing import List, Dict, Any, Optional

from efficient_context import ContextManager
from efficient_context.compression import SemanticDeduplicator
from efficient_context.chunking import SemanticChunker
from efficient_context.retrieval import CPUOptimizedRetriever

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightLLM:
    """
    A simple wrapper for a lightweight LLM.
    
    This is a placeholder that would be replaced with an actual
    lightweight LLM implementation in a real application.
    """
    
    def __init__(self, model_name: str = "tiny-llm"):
        """
        Initialize the lightweight LLM.
        
        Args:
            model_name: Name of the model to use
        """
        self.model_name = model_name
        logger.info(f"Initialized LightweightLLM with model: {model_name}")
        
        # This would be where you'd load your model in a real implementation
        logger.info("Note: This is a placeholder class for demonstration purposes")
    
    def generate(
        self, 
        prompt: str, 
        context: Optional[str] = None, 
        max_tokens: int = 512
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The prompt for generation
            context: Optional context to condition the generation
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            response: Generated text response
        """
        # This is a fake implementation for demonstration
        # In a real application, you'd call your LLM here
        
        logger.info(f"Generating response with context size: {len(context.split()) if context else 0} tokens")
        
        # Simulate generation time based on context size
        if context:
            time.sleep(0.001 * len(context.split()))  # Simulate processing time
            
            # Simple keyword detection for demo purposes
            if "renewable energy" in context and "climate" in context:
                return "Renewable energy has a positive impact on climate change mitigation by reducing greenhouse gas emissions. The transition from fossil fuels to renewable sources like wind and solar is crucial for limiting global warming."
            elif "rural" in context and "renewable" in context:
                return "Renewable energy technologies are well-suited for rural and remote areas. They can provide decentralized power generation, improving energy access in areas without reliable grid connections, which is critical for human development."
            else:
                return "Renewable energy sources are sustainable alternatives to fossil fuels. They include solar, wind, hydro, geothermal, and biomass energy, and their use is growing globally."
        else:
            return "I don't have enough context to provide a detailed answer on this topic."

def main():
    # Sample documents - in a real application, you might load these from files
    documents = [
        {
            "content": """
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
            """,
            "metadata": {"topic": "renewable energy", "source": "example"}
        },
        {
            "content": """
            Climate change mitigation consists of actions to limit global warming and its related effects.
            This involves reductions in human emissions of greenhouse gases (GHGs) as well as activities 
            that reduce their concentration in the atmosphere.
            
            Fossil fuels account for more than 70% of GHG emissions. The energy sector contributes to global 
            emissions, mainly through the burning of fossil fuels to generate electricity and heat, 
            and through the use of gasoline and diesel to power vehicles.
            
            A transition to renewable energy is a key component of climate change mitigation. By replacing 
            fossil fuel power plants with renewable energy sources, such as wind and solar, we can reduce 
            the amount of greenhouse gases emitted into the atmosphere.
            
            Renewable energy can also play a role in adapting to climate change, for example by providing 
            reliable power for cooling in increasingly hot regions, or by ensuring energy access in the 
            aftermath of climate-related disasters.
            """,
            "metadata": {"topic": "climate change", "source": "example"}
        },
    ]
    
    # Initialize a context manager with custom strategies
    context_manager = ContextManager(
        compressor=SemanticDeduplicator(threshold=0.85),
        chunker=SemanticChunker(chunk_size=256),
        retriever=CPUOptimizedRetriever(embedding_model="lightweight"),
        max_context_size=512  # Intentionally small for demonstration
    )
    
    # Initialize a lightweight LLM
    llm = LightweightLLM()
    
    # Add documents to the context manager
    document_ids = context_manager.add_documents(documents)
    
    # Example queries
    queries = [
        "Tell me about the climate impact of renewable energy",
        "How does renewable energy work in rural areas?",
        "What are the advantages of using renewable energy?"
    ]
    
    # Process each query
    for query in queries:
        print(f"\n\n=== QUERY: {query} ===")
        
        # Generate optimized context for the query
        start_time = time.time()
        optimized_context = context_manager.generate_context(query=query)
        context_time = time.time() - start_time
        
        print(f"Context generation took {context_time:.3f} seconds")
        print(f"Context size: {len(optimized_context.split())} tokens")
        
        # Generate response using the LLM with the optimized context
        start_time = time.time()
        response = llm.generate(prompt=query, context=optimized_context)
        llm_time = time.time() - start_time
        
        print(f"LLM generation took {llm_time:.3f} seconds")
        print(f"--- RESPONSE ---")
        print(response)
        print("-" * 50)

if __name__ == "__main__":
    main()
