#!/usr/bin/env python3

"""
Anki Export Comparison Tool - Diff CLI Entry Point
"""

import sys
from ..core.diff import main

def cli_main():
    """CLI entry point for anki-diff command."""
    return main()

if __name__ == "__main__":
    sys.exit(cli_main())