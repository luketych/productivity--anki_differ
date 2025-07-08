#!/usr/bin/env python3

"""
Anki Export Comparison Tool - Web Interface CLI Entry Point
"""

def cli_main():
    """CLI entry point for anki-web command."""
    from ..web.app import app
    app.run(debug=True, port=5001)

if __name__ == "__main__":
    cli_main()