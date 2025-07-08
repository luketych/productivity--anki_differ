# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

### With uv (Recommended)
```bash
# Install the project in development mode
uv sync --dev

# Run the web interface
uv run anki-web

# Open browser to http://127.0.0.1:5001
```

### Command Line Tools (with uv)
```bash
# Basic comparison
uv run anki-diff <file1> <file2>

# Merge with conflict resolution
uv run anki-merge <file1> <file2> <output_file>

# Selective merge operations
uv run anki-selective extract-overlapping <file1> <file2> <output_file>
uv run anki-selective generate-selection <file1> <file2> <output_prefix>
uv run anki-selective create-merged-export <file1> <file2> <selection_file> <output_file>
```

### Legacy Installation (without uv)
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask

# Run the web app directly
python -m anki_differ.cli.web
```

## High-Level Architecture

### Data Flow
1. **Input**: Two Anki export files (tab-separated format with `#separator:tab` header)
2. **Comparison**: Cards are matched by question text, categorized as:
   - Identical (same question & answer)
   - Different (same question, different answer)
   - Unique to file1/file2
3. **Selection**: Users choose which version to keep via web UI or CLI
4. **Output**: Merged Anki export file preserving the original format

### Key Components

**Web Application** (`/src/anki_differ/web/app.py`):
- Flask app serving the web interface
- Routes: `/` (upload), `/select` (card selection), `/generate_export` (download)
- Data persisted in `/src/data/comparison_data.json` between requests
- Templates in `/templates/` directory

**Core Logic** (`/src/anki_differ/core/`):
- Card parsing: Handles multi-line content and malformed inputs
- Question-based matching: Questions serve as unique identifiers
- Default selections: All cards included by default, conflicts default to file1

**File Structure**:
- Entry points: uv commands (`anki-web`, `anki-diff`, `anki-merge`, `anki-selective`)
- Implementation: `/src/anki_differ/` proper Python package structure
- CLI modules: `/src/anki_differ/cli/` for command-line interfaces
- Core modules: `/src/anki_differ/core/` for business logic
- Web modules: `/src/anki_differ/web/` for web interface
- Data storage: `/src/data/` for comparison results, `/src/uploads/` for uploaded files

### Important Implementation Details

- The web app is stateful, storing comparison data in JSON between requests
- Cards can contain HTML content which is preserved
- The comparison uses exact string matching on questions
- File headers (lines starting with `#`) are preserved from file1 by default
- Bootstrap 5.3 is used for the UI with tab-based navigation