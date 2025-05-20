"""
Manual benchmark for the SemanticDeduplicator component.
"""

import sys
import logging
from efficient_context.compression import SemanticDeduplicator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("Testing SemanticDeduplicator")
    
    # Create a repetitive document with semantically similar sentences
    repetitive_text = """
    Climate change is a significant global challenge.
    Global warming is affecting ecosystems worldwide.
    The Earth's temperature is rising due to human activities.
    Climate change poses a serious threat to our planet.
    Rising global temperatures are causing environmental problems.
    
    Renewable energy is key to a sustainable future.
    Clean energy sources help reduce carbon emissions.
    Sustainable power generation is vital for fighting climate change.
    Green energy technologies are becoming more affordable.
    Renewable resources provide alternatives to fossil fuels.
    """
    
    print(f"Original text length: {len(repetitive_text.split())} words")
    
    # Test with different thresholds
    for threshold in [0.7, 0.8, 0.85, 0.9, 0.95]:
        print(f"\nTesting threshold: {threshold}")
        
        deduplicator = SemanticDeduplicator(threshold=threshold)
        
        # Apply deduplication
        compressed_text = deduplicator.compress(repetitive_text)
        
        print(f"Compressed text length: {len(compressed_text.split())} words")
        print(f"Compression ratio: {len(compressed_text.split()) / len(repetitive_text.split()):.2f}")
        
        # Print the first 100 characters of the compressed text
        print(f"Compressed text (preview): {compressed_text[:100]}...")

if __name__ == "__main__":
    main()
