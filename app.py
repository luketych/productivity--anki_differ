#!/usr/bin/env python3

"""
Anki Export Comparison Tool - Web Interface Entry Point

This is the entry point for the web-based interface of the Anki Export Comparison Tool.
It imports and runs the actual application from the src directory.
"""

if __name__ == "__main__":
    from src.web_app import app
    app.run(debug=True, port=5001)
