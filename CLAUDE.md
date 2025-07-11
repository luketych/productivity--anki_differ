# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Anki Export Comparison Tool (anki-diff-tool) - a Python package that helps compare, analyze, and merge Anki export files from different sources (macOS, Android, Anki Web). The tool provides both command-line interfaces and a web-based UI for interactive card comparison and selective merging.

## Key Commands

**IMPORTANT**: Use `uv` for all Python commands. Do not use `python` or `python3` directly.

### Development
- **Install dependencies**: `uv pip install -e .` (installs in development mode)
- **Run tests**: `uv run pytest` (runs all tests in tests/ directory)
- **Run specific test types**: 
  - `uv run pytest tests/unit/` (unit tests only)
  - `uv run pytest tests/integration/` (integration tests only)
  - `uv run pytest tests/e2e/` (end-to-end tests only)
- **Run single test**: `uv run pytest tests/unit/test_specific.py::test_function`

### CLI Usage
- **Diff command**: `anki-diff <file1> <file2>`
- **Merge command**: `anki-merge <file1> <file2> <output_file>`
- **Selective merge**: `anki-selective extract-overlapping <file1> <file2> <output_file>`
- **Web interface**: `anki-web` (starts Flask server on http://127.0.0.1:5000)

### Legacy Commands (still functional)
- **Basic comparison**: `uv run python anki_diff.py <file1> <file2>`
- **Merge exports**: `uv run python merge_exports.py <file1> <file2> <output_file>`
- **Web interface**: `uv run python app.py`

## Architecture

### Package Structure
- **src/anki_differ/**: Main package with proper Python package organization
- **src/anki_differ/cli/**: Command-line interfaces (diff, merge, selective, web)
- **src/anki_differ/core/**: Core functionality (diff algorithms, merge logic)
- **src/anki_differ/web/**: Flask web application for visual interface

### Core Components
- **Diff Engine** (`src/anki_differ/core/diff.py`): Main comparison logic with functions like `load_anki_export()`, `parse_anki_export()`, `find_missing_cards()`
- **Web Interface** (`src/anki_differ/web/app.py`): Flask-based UI for file upload, comparison visualization, and selective merging
- **CLI Entry Points** (`src/anki_differ/cli/main.py`): Unified command-line interface with subcommands

### Test Architecture
- **Unit Tests** (`tests/unit/`): Fast, isolated tests for individual functions (target: 90% coverage)
- **Integration Tests** (`tests/integration/`): API endpoints and system components (target: 85% coverage)
- **E2E Tests** (`tests/e2e/`): Complete user workflows with browser automation
- **Performance Tests** (`tests/performance/`): Load testing and benchmarking
- **Test Fixtures** (`tests/fixtures/`): Includes `test_data_factory.py` for generating test datasets

### Configuration
- **Build System**: Uses `pyproject.toml` with Hatchling
- **Testing**: Configured with `pytest.ini` supporting markers (unit, integration, e2e, performance, slow)
- **Dependencies**: Flask, requests>=2.32.4 (Python >=3.8 required)

## Current Development

- **Active Branch**: `feature/similar_cards` - implementing similar card matching functionality
- **Purpose**: Identify similar cards across exports with configurable similarity thresholds
- **Status**: Feature development in progress

## Important Notes

- The project uses modern Python package structure with proper src/ layout
- All CLI commands are defined in `pyproject.toml` as entry points
- Test framework is comprehensive with clear separation of test types
- Web interface provides visual card comparison and interactive selection
- The tool handles Unicode characters and large datasets
- Session management and temporary file cleanup are handled by the web interface