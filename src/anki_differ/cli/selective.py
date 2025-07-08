#!/usr/bin/env python3

"""
Anki Export Comparison Tool - Selective Merge CLI Entry Point
"""

import sys
from ..core.selective import main

def cli_main():
    """CLI entry point for anki-selective command."""
    return main()

if __name__ == "__main__":
    sys.exit(cli_main())