#!/usr/bin/env python3

"""
Anki Export Comparison Tool - Merge CLI Entry Point
"""

import sys
from ..core.merge import main

def cli_main():
    """CLI entry point for anki-merge command."""
    return main()

if __name__ == "__main__":
    sys.exit(cli_main())