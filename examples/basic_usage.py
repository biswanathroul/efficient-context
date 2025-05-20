"""
Example usage of efficient-context library.
"""

import logging
from efficient_context import ContextManager
from efficient_context.compression import SemanticDeduplicator
from efficient_context.chunking import SemanticChunker
from efficient_context.retrieval import CPUOptimizedRetriever
from efficient_context.memory import MemoryManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Sample documents
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
        memory_manager=MemoryManager(target_usage_percent=80.0),
        max_context_size=1024
    )
    
    # Add documents to the context manager
    document_ids = context_manager.add_documents(documents)
    
    # Query 1: Generate optimized context for a query
    query1 = "Tell me about the climate impact of renewable energy"
    print(f"\n\n=== QUERY: {query1} ===")
    optimized_context1 = context_manager.generate_context(query=query1)
    print(f"--- OPTIMIZED CONTEXT ({len(optimized_context1.split())} tokens) ---")
    print(optimized_context1)
    
    # Query 2: Different topic
    query2 = "How does renewable energy work in rural areas?"
    print(f"\n\n=== QUERY: {query2} ===")
    optimized_context2 = context_manager.generate_context(query=query2)
    print(f"--- OPTIMIZED CONTEXT ({len(optimized_context2.split())} tokens) ---")
    print(optimized_context2)
    
    # Example of using with an LLM (commented out since we don't have an actual LLM here)
    # response = your_llm_model.generate(prompt="Answer this question using the provided context.", context=optimized_context)
    # print(f"LLM Response: {response}")

if __name__ == "__main__":
    main()
