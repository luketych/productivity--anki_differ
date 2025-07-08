#!/usr/bin/env python3

"""
Anki Export Comparison Tool - Merge Exports Entry Point

This is the entry point for the merge exports tool of the Anki Export Comparison Tool.
It imports and runs the actual tool from the src directory.
"""

import sys
from src.merge_exports import main

if __name__ == "__main__":
    sys.exit(main())
