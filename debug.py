#!/usr/bin/env python
"""
Debug script for efficient-context.
"""

import sys
import os

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    import efficient_context
    print(f"Successfully imported efficient_context: {efficient_context.__file__}")
except ImportError as e:
    print(f"Failed to import efficient_context: {e}")

print("Script completed")
