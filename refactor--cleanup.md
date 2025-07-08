# Refactor/Cleanup Branch Analysis

## Overview
The refactor/cleanup branch represents the current state of the project after significant modifications. This branch contains substantial deletions and structural changes that appear to have broken the application's functionality.

## Current State (Issues Identified)

### Major Problems
1. **Massive File Deletions**: 40+ files have been deleted from the repository
2. **Broken Functionality**: The application structure has been compromised
3. **Inconsistent State**: Many core files are missing while some remain

### Deleted Files (Critical Issues)
- **Legacy Scripts**: `anki_diff.py`, `anki_diff_tool.py`, `app.py`, `web_app.py`
- **Core Modules**: `src/anki_diff.py`, `src/anki_diff_tool.py`, `src/merge_exports.py`
- **Documentation**: `MILESTONES.md`, `PROJECT_OBJECTIVE.md`, `TESTING_STRATEGY.md`
- **Test Files**: `demo_tests.py`, `run_tests.py`, `test_manual.py`, `test_ui.py`
- **Build Artifacts**: All `anki_diff_tool.egg-info/` files
- **Template Backups**: Multiple `select.html` backup files
- **UI Debug Files**: `tab_test.html`, `view_differences.html`, debug templates

### Remaining Structure (What Still Works)
- **Package Structure**: `src/anki_differ/` directory with proper Python package layout
- **Core Logic**: Core modules in `src/anki_differ/core/`
- **CLI Interface**: CLI modules in `src/anki_differ/cli/`
- **Web Interface**: Flask app in `src/anki_differ/web/app.py`
- **Templates**: Main templates (`index.html`, `select.html`)
- **Tests**: Comprehensive test suite in `tests/` directory

## Current Architecture (What's Left)

### Technologies Still Used
- **Python 3.8+**: Base language
- **Flask**: Web framework (still functional)
- **Bootstrap 5.3**: CSS framework for UI
- **uv**: Package manager
- **pytest**: Testing framework

### Package Structure (Intact)
```
src/anki_differ/
├── __init__.py
├── cli/
│   ├── __init__.py
│   ├── diff.py
│   ├── main.py
│   ├── merge.py
│   ├── selective.py
│   └── web.py
├── core/
│   ├── __init__.py
│   ├── diff.py
│   ├── merge.py
│   └── selective.py
└── web/
    ├── __init__.py
    └── app.py
```

### Web Application Status
- **Flask App**: Still exists at `src/anki_differ/web/app.py`
- **Templates**: Core templates remain (`index.html`, `select.html`)
- **Functionality**: Same features as main branch (if working)
- **UI**: Bootstrap-based responsive design

## Git Status Analysis

### Modified Files
- `.claude/settings.local.json`: Configuration changes
- `CLAUDE.md`: Documentation updates
- `pyproject.toml`: Build configuration changes
- `src/data/comparison_data.json`: Data file modifications
- `uv.lock`: Dependency lock file changes

### Untracked Files (Potential Issues)
- `descripitions/`: New directory (possible typo - should be "descriptions")
- `src/anki_differ/`: Package structure (should be tracked)
- Various test files: `test_*.py` files not in git
- `tests/`: Test directory structure

## Critical Issues

### 1. Package Not Tracked
The main package `src/anki_differ/` is showing as untracked (??) in git status, indicating it may not be properly committed.

### 2. Inconsistent Dependencies
The `uv.lock` file has been modified, potentially indicating dependency issues.

### 3. Missing Legacy Code
While the new package structure exists, the removal of legacy files may have broken backward compatibility or transition processes.

### 4. Test Suite Status
Many test files are untracked, suggesting the test suite may not be properly integrated.

## Comparison with Main Branch

### What's Different
1. **Structure**: Same modern package structure remains
2. **Functionality**: Should be identical (if working)
3. **Code Quality**: Same codebase in core modules
4. **File Organization**: Many legacy files removed

### What's Broken
1. **Git Tracking**: Package not properly tracked
2. **Legacy Support**: Old scripts removed
3. **Development Files**: Debug and backup files removed
4. **Documentation**: Project documentation removed

## Recommendations

### Immediate Actions Needed
1. **Restore Git Tracking**: Add `src/anki_differ/` to git
2. **Test Functionality**: Verify the application still works
3. **Restore Documentation**: Add back critical documentation
4. **Fix Dependencies**: Ensure uv.lock is consistent

### Code Quality Assessment
- **Core Logic**: Appears intact and functional
- **Web Interface**: Flask app should work if properly configured
- **CLI Tools**: Should be functional via uv commands
- **Tests**: Test suite exists but may need integration

## Current Functionality Status
Based on the remaining files, the application should theoretically work with:
- `uv run anki-web`: Launch web interface
- `uv run anki-diff`: CLI comparison tool
- `uv run anki-merge`: CLI merge tool
- `uv run anki-selective`: Advanced operations

However, the git tracking issues and untracked package structure suggest the application may not be properly deployable or runnable.

## Summary
The refactor/cleanup branch has the same core functionality as main but with significant structural issues that have likely broken the application. The cleanup was too aggressive, removing necessary files and breaking git tracking. The branch needs immediate attention to restore functionality while maintaining the improved package structure.