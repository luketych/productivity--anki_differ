#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for Anki Diff Tool tests
"""

import pytest
import os
import sys
import tempfile
import shutil
from typing import Generator

# Add project root to Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Import after path setup
from tests.fixtures.test_data_factory import TestDataFactory, TestFixtures
from src.web_app import app

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (medium speed, some dependencies)"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests (slow, full system)"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests (slow, resource intensive)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on location"""
    for item in items:
        # Add markers based on test file location
        if "unit" in item.fspath.dirname:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.fspath.dirname:
            item.add_marker(pytest.mark.integration)
        elif "e2e" in item.fspath.dirname:
            item.add_marker(pytest.mark.e2e)
        elif "performance" in item.fspath.dirname:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)

@pytest.fixture(scope="session")
def project_root_dir():
    """Provide project root directory"""
    return os.path.join(os.path.dirname(__file__), '..')

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory"""
    return os.path.join(os.path.dirname(__file__), 'fixtures')

@pytest.fixture
def temp_dir():
    """Provide temporary directory that's cleaned up after test"""
    temp_path = tempfile.mkdtemp(prefix='anki_test_')
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def temp_file():
    """Provide temporary file that's cleaned up after test"""
    fd, temp_path = tempfile.mkstemp(prefix='anki_test_', suffix='.txt')
    os.close(fd)  # Close the file descriptor
    yield temp_path
    try:
        os.unlink(temp_path)
    except OSError:
        pass

@pytest.fixture
def sample_datasets():
    """Provide sample test datasets"""
    return {
        'tiny': TestFixtures.tiny_normal(),
        'small': TestFixtures.small_normal(),
        'edge_cases': TestFixtures.edge_cases(),
        'no_overlap': TestFixtures.no_overlap(),
        'identical_only': TestFixtures.identical_only(),
        'different_only': TestFixtures.different_only(),
        'unique_only': TestFixtures.unique_only()
    }

@pytest.fixture
def sample_comparison_data(sample_datasets):
    """Provide sample comparison data in JSON format"""
    return {
        name: TestDataFactory.dataset_to_comparison_data(dataset)
        for name, dataset in sample_datasets.items()
    }

@pytest.fixture
def sample_anki_files(sample_datasets, temp_dir):
    """Provide sample Anki export files"""
    files = {}
    
    for name, dataset in sample_datasets.items():
        file1_content, file2_content = TestDataFactory.dataset_to_anki_files(dataset)
        
        file1_path = os.path.join(temp_dir, f'{name}_file1.txt')
        file2_path = os.path.join(temp_dir, f'{name}_file2.txt')
        
        with open(file1_path, 'w', encoding='utf-8') as f:
            f.write(file1_content)
        
        with open(file2_path, 'w', encoding='utf-8') as f:
            f.write(file2_content)
        
        files[name] = (file1_path, file2_path)
    
    yield files

@pytest.fixture
def flask_app():
    """Provide configured Flask app for testing"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def flask_client(flask_app, temp_dir):
    """Provide Flask test client with temporary directories"""
    flask_app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
    flask_app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
    
    os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(flask_app.config['DATA_FOLDER'], exist_ok=True)
    
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

@pytest.fixture
def populated_flask_client(flask_client, sample_comparison_data):
    """Provide Flask client with pre-populated test data"""
    # Use small normal dataset as default
    comparison_data = sample_comparison_data['small']
    
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    with open(data_file, 'w') as f:
        import json
        json.dump(comparison_data, f)
    
    yield flask_client

# Skip decorators for different test types
skip_if_no_browser = pytest.mark.skipif(
    not shutil.which('chromedriver') and not shutil.which('chrome'),
    reason="Chrome/ChromeDriver not available for browser tests"
)

skip_if_no_display = pytest.mark.skipif(
    os.environ.get('DISPLAY') is None and os.name != 'nt',
    reason="No display available for GUI tests"
)

skip_if_low_memory = pytest.mark.skipif(
    os.environ.get('PYTEST_SKIP_MEMORY_TESTS') == '1',
    reason="Memory tests skipped due to environment setting"
)

# Performance test configuration
@pytest.fixture
def performance_config():
    """Configuration for performance tests"""
    return {
        'max_processing_time': {
            'small': 1.0,    # seconds
            'medium': 5.0,   # seconds  
            'large': 30.0    # seconds
        },
        'max_memory_usage': {
            'small': 50,     # MB
            'medium': 100,   # MB
            'large': 500     # MB
        },
        'concurrent_users': 10,
        'operations_per_user': 3
    }

# Test utilities
class TestUtils:
    """Utility functions for tests"""
    
    @staticmethod
    def assert_anki_export_format(content: str):
        """Assert that content is in valid Anki export format"""
        lines = content.strip().split('\n')
        
        # Should have at least headers
        header_lines = [line for line in lines if line.startswith('#')]
        assert len(header_lines) > 0, "Should have header lines"
        
        # Card lines should have exactly one tab
        card_lines = [line for line in lines if '\t' in line and not line.startswith('#')]
        for line in card_lines:
            assert line.count('\t') == 1, f"Card line should have exactly one tab: {line}"
    
    @staticmethod
    def count_cards_by_type(comparison_data: dict) -> dict:
        """Count cards by type in comparison data"""
        return {
            'identical': len(comparison_data.get('identical_cards', [])),
            'different': len(comparison_data.get('different_cards', [])),
            'unique_file1': len(comparison_data.get('unique_file1', [])),
            'unique_file2': len(comparison_data.get('unique_file2', []))
        }
    
    @staticmethod
    def validate_comparison_data_structure(data: dict):
        """Validate comparison data has correct structure"""
        required_keys = ['identical_cards', 'different_cards', 'unique_file1', 'unique_file2', 'stats']
        
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
        
        # Validate stats match actual data
        stats = data['stats']
        actual_counts = TestUtils.count_cards_by_type(data)
        
        assert stats['identical'] == actual_counts['identical'], "Identical count mismatch"
        assert stats['different'] == actual_counts['different'], "Different count mismatch"
        assert stats['only_file1'] == actual_counts['unique_file1'], "Unique file1 count mismatch"
        assert stats['only_file2'] == actual_counts['unique_file2'], "Unique file2 count mismatch"

# Make TestUtils available as fixture
@pytest.fixture
def test_utils():
    """Provide test utilities"""
    return TestUtils

# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically cleanup temporary files after each test"""
    yield
    # Cleanup any remaining temp files with our prefix
    import glob
    temp_files = glob.glob('/tmp/anki_test_*') + glob.glob('/tmp/anki_e2e_*')
    for temp_file in temp_files:
        try:
            if os.path.isfile(temp_file):
                os.unlink(temp_file)
            elif os.path.isdir(temp_file):
                shutil.rmtree(temp_file, ignore_errors=True)
        except OSError:
            pass  # Ignore cleanup errors