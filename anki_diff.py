#!/usr/bin/env python3

"""
Anki Export Comparison Tool - Anki Diff Entry Point

This is the entry point for the comparison tool of the Anki Export Comparison Tool.
It imports and runs the actual tool from the src directory.
"""

import sys
from src.anki_diff import main

if __name__ == "__main__":
    sys.exit(main())
