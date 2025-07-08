# Main Branch Analysis

## Overview
The main branch contains a working Anki export comparison and merging tool with both CLI and web interfaces. The application allows users to upload two Anki export files, compare them, and create a merged version by selecting which cards to keep.

## Architecture

### Project Structure
- **Package Structure**: Modern Python package with `src/` layout
- **Entry Points**: Defined in `pyproject.toml` with CLI commands
- **Web Interface**: Flask-based web application
- **Core Logic**: Separated into dedicated modules

### Key Directories
```
src/anki_differ/
├── cli/          # Command-line interfaces
├── core/         # Core business logic
└── web/          # Web application
templates/        # HTML templates
tests/           # Test suite with multiple categories
```

## Technologies Used

### Core Technologies
- **Python 3.8+**: Base language
- **Flask**: Web framework for the web interface
- **Hatchling**: Modern Python build system
- **uv**: Package manager and dependency resolution

### Frontend Technologies
- **Bootstrap 5.3**: CSS framework for responsive UI
- **Vanilla JavaScript**: Client-side interactions
- **HTML5 Templates**: Jinja2 templating

### Development Tools
- **pytest**: Testing framework
- **uv**: Development dependency management

## Key Features

### CLI Tools
- `anki-diff`: Basic file comparison
- `anki-merge`: Merge with conflict resolution
- `anki-selective`: Advanced selective merging operations
- `anki-web`: Launch web interface

### Web Interface
- File upload interface
- Card comparison and selection
- Export generation
- Bootstrap-based responsive design

### Core Functionality
- **File Parsing**: Handles Anki export format with tab separators
- **Card Matching**: Uses question text as unique identifier
- **Comparison Logic**: Categorizes cards as identical, different, or unique
- **Malformed Data Handling**: Robust parsing with multi-line content support
- **Export Generation**: Creates properly formatted Anki export files

## Data Flow

1. **Upload**: Two Anki export files uploaded via web interface
2. **Parsing**: Files parsed into headers and card pairs (question, answer)
3. **Comparison**: Cards categorized into:
   - Identical cards (same question and answer)
   - Different cards (same question, different answers)
   - Unique cards (only in one file)
4. **Selection**: User selects which version to keep for conflicts
5. **Export**: Merged file generated with user selections

## Technical Implementation

### File Format Support
- **Headers**: Lines starting with `#` (e.g., `#separator:tab`)
- **Cards**: Tab-separated question-answer pairs
- **Encoding**: UTF-8 with proper handling of HTML content

### State Management
- **Persistence**: JSON file storage for comparison data
- **Session State**: Maintained between web requests
- **File Storage**: Uploaded files stored in configured directories

### Error Handling
- **Malformed Input**: Robust parsing with warnings
- **Missing Files**: Proper error responses
- **Invalid Data**: Graceful degradation

## Testing Strategy
- **Unit Tests**: Core function testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Complete user workflow testing
- **Performance Tests**: Load testing capabilities
- **Test Fixtures**: Comprehensive test data

## Configuration
- **Environment Variables**: Configurable paths and settings
- **Default Values**: Sensible defaults for common use cases
- **Security**: Secure file handling with werkzeug utilities

## Key Strengths
1. **Proper Package Structure**: Modern Python packaging standards
2. **Separation of Concerns**: Clear separation between CLI, web, and core logic
3. **Comprehensive Testing**: Multiple test categories and fixtures
4. **Robust Parsing**: Handles edge cases and malformed data
5. **User-Friendly Interface**: Clean Bootstrap-based UI
6. **Multiple Access Methods**: Both CLI and web interfaces available