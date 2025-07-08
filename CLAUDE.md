# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

### Web Interface (Recommended)
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask

# Run the web app
python app.py

# Open browser to http://127.0.0.1:5000
```

### Command Line Tools
```bash
# Basic comparison
python3 anki_diff.py <file1> <file2>

# Merge with conflict resolution
python3 merge_exports.py <file1> <file2> <output_file>

# Selective merge operations
python3 selective_merge.py extract-overlapping <file1> <file2> <output_file>
python3 selective_merge.py generate-selection <file1> <file2> <output_prefix>
python3 selective_merge.py create-merged-export <file1> <file2> <selection_file> <output_file>
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

**Web Application** (`/src/web_app.py`):
- Flask app serving the web interface
- Routes: `/` (upload), `/select` (card selection), `/generate_export` (download)
- Data persisted in `/src/data/comparison_data.json` between requests
- Templates in `/templates/` directory

**Core Logic**:
- Card parsing: Handles multi-line content and malformed inputs
- Question-based matching: Questions serve as unique identifiers
- Default selections: All cards included by default, conflicts default to file1

**File Structure**:
- Entry points: `app.py` (web), `anki_diff.py`, `merge_exports.py`, `selective_merge.py` (CLI)
- Implementation: `/src/` directory contains the actual logic
- Data storage: `/src/data/` for comparison results, `/src/uploads/` for uploaded files

### Important Implementation Details

- The web app is stateful, storing comparison data in JSON between requests
- Cards can contain HTML content which is preserved
- The comparison uses exact string matching on questions
- File headers (lines starting with `#`) are preserved from file1 by default
- Bootstrap 5.3 is used for the UI with tab-based navigation