#!/usr/bin/env python3

"""
Anki Export Comparison Tool - Unified Tool Entry Point

This is the entry point for the unified tool launcher of the Anki Export Comparison Tool.
It imports and runs the actual tool from the src directory.
"""

import sys
from src.anki_diff_tool import main

if __name__ == "__main__":
    sys.exit(main())
