#!/usr/bin/env python3

"""
Anki Export Comparison Tool - Selective Merge Entry Point

This is the entry point for the selective merge tool of the Anki Export Comparison Tool.
It imports and runs the actual tool from the src directory.
"""

import sys
from src.selective_merge import main

if __name__ == "__main__":
    sys.exit(main())
