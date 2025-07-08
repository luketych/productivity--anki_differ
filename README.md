# Anki Export Comparison Tool

This tool helps you compare, analyze, and merge Anki export files from different sources (like macOS and Android). It was created to resolve mismatches between Anki Web and Android app exports.

## Features

- **Comparison Tools**
  - Identifies missing cards between exports
  - Detects content differences in shared cards
  - Provides detailed reports of all differences

- **Merging Capabilities**
  - Merge two export files with conflict resolution
  - Extract overlapping cards from both exports
  - Selective merging with custom selection of card versions

- **Visual Interface**
  - Web-based UI for easy card comparison and selection
  - Side-by-side diff view for comparing card content
  - Interactive selection of which card version to keep

## Usage Options

### Command Line Tools

**Basic Comparison:**
```bash
python3 anki_diff.py <file1> <file2>
```

**Merge Exports:**
```bash
python3 merge_exports.py <file1> <file2> <output_file>
```

**Selective Merge:**
```bash
python3 selective_merge.py extract-overlapping <file1> <file2> <output_file>
python3 selective_merge.py generate-selection <file1> <file2> <output_prefix>
python3 selective_merge.py create-merged-export <file1> <file2> <selection_file> <output_file>
```

### Web Interface (NEW!)
```bash
python3 app.py
```
Then open your browser to http://127.0.0.1:5000

## Output

The tool provides:
1. Console summaries of operations
2. Detailed text reports
3. Interactive web UI for card selection
4. Merged Anki export files ready for import

## Project Components

- `anki_diff.py`: Core comparison script
- `merge_exports.py`: Basic merge functionality
- `selective_merge.py`: Advanced selective merging
- `anki_diff_tool.py`: Unified command-line launcher
- `app.py`: Web-based interface for visual comparison and selection
- `templates/`: HTML templates for web interface
