#!/usr/bin/env python3
"""
Integration Tests for Anki Diff API Endpoints
Tests the Flask application endpoints with real data flows
"""

import pytest
import os
import sys
import tempfile
import json
import shutil
from io import BytesIO

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.web_app import app
from tests.fixtures.test_data_factory import TestDataFactory, DatasetSize, ScenarioType, TestFixtures

class TestAppConfiguration:
    """Test Flask app configuration and setup"""
    
    @pytest.fixture
    def client(self):
        """Create test client with temporary directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
            
            # Create directories
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            with app.test_client() as client:
                with app.app_context():
                    yield client
    
    def test_app_config(self, client):
        """Test that app is properly configured for testing"""
        assert app.config['TESTING'] is True
        assert os.path.exists(app.config['UPLOAD_FOLDER'])
        assert os.path.exists(app.config['DATA_FOLDER'])

class TestIndexRoute:
    """Test the index route and basic navigation"""
    
    @pytest.fixture
    def client(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            with app.test_client() as client:
                with app.app_context():
                    yield client
    
    def test_index_without_data(self, client):
        """Test index route when no comparison data exists"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'html' in response.data  # Should return the upload form
    
    def test_index_with_existing_data(self, client):
        """Test index route when comparison data already exists"""
        # Create comparison data
        dataset = TestFixtures.small_normal()
        comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
        
        data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
        with open(data_file, 'w') as f:
            json.dump(comparison_data, f)
        
        response = client.get('/')
        # Should redirect to select page
        assert response.status_code == 302
        assert '/select' in response.headers['Location']

class TestUploadRoute:
    """Test file upload functionality"""
    
    @pytest.fixture
    def client(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            with app.test_client() as client:
                with app.app_context():
                    yield client
    
    def test_upload_valid_files(self, client):
        """Test uploading valid Anki export files"""
        dataset = TestFixtures.small_normal()
        file1_content, file2_content = TestDataFactory.dataset_to_anki_files(dataset)
        
        data = {
            'file1': (BytesIO(file1_content.encode('utf-8')), 'test1.txt'),
            'file2': (BytesIO(file2_content.encode('utf-8')), 'test2.txt'),
            'file1_name': 'Test File 1',
            'file2_name': 'Test File 2'
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        # Should redirect to select page
        assert response.status_code == 302
        assert '/select' in response.headers['Location']
        
        # Should create comparison data
        data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
        assert os.path.exists(data_file)
        
        with open(data_file, 'r') as f:
            comparison_data = json.load(f)
        
        assert 'stats' in comparison_data
        assert comparison_data['file1_name'] == 'Test File 1'
        assert comparison_data['file2_name'] == 'Test File 2'
    
    def test_upload_missing_files(self, client):
        """Test upload with missing files"""
        data = {
            'file1_name': 'Test File 1',
            'file2_name': 'Test File 2'
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_upload_empty_files(self, client):
        """Test upload with empty files"""
        data = {
            'file1': (BytesIO(b''), ''),
            'file2': (BytesIO(b''), ''),
            'file1_name': 'Test File 1',
            'file2_name': 'Test File 2'
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_upload_large_files(self, client):
        """Test upload with large files"""
        dataset = TestDataFactory.create_dataset(DatasetSize.LARGE, ScenarioType.NORMAL)
        file1_content, file2_content = TestDataFactory.dataset_to_anki_files(dataset)
        
        data = {
            'file1': (BytesIO(file1_content.encode('utf-8')), 'large1.txt'),
            'file2': (BytesIO(file2_content.encode('utf-8')), 'large2.txt'),
            'file1_name': 'Large File 1',
            'file2_name': 'Large File 2'
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        # Should handle large files successfully
        assert response.status_code == 302
        
        # Verify data was processed correctly
        data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
        assert os.path.exists(data_file)

class TestSelectRoutes:
    """Test card selection routes"""
    
    @pytest.fixture
    def client_with_data(self):
        """Client with pre-loaded comparison data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            # Create test data
            dataset = TestFixtures.small_normal()
            comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
            
            data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
            with open(data_file, 'w') as f:
                json.dump(comparison_data, f)
            
            with app.test_client() as client:
                with app.app_context():
                    yield client
    
    def test_select_with_data(self, client_with_data):
        """Test select route with existing data"""
        response = client_with_data.get('/select')
        
        assert response.status_code == 200
        assert b'Anki Diff' in response.data
        assert b'tab' in response.data  # Should have tab navigation
    
    def test_select_new_with_data(self, client_with_data):
        """Test enhanced select route with existing data"""
        response = client_with_data.get('/select-new')
        
        assert response.status_code == 200
        assert b'Enhanced UI' in response.data
        assert b'debug' in response.data.lower()  # Should have debug features
        assert b'AnkiDiffUI' in response.data  # Should have JavaScript class
    
    def test_select_without_data(self):
        """Test select route without existing data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            with app.test_client() as client:
                response = client.get('/select')
                
                # Should redirect to index
                assert response.status_code == 302
                assert '/' in response.headers['Location']

class TestDataPersistence:
    """Test data saving and persistence"""
    
    @pytest.fixture
    def client_with_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            # Create test data
            dataset = TestFixtures.small_normal()
            comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
            
            data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
            with open(data_file, 'w') as f:
                json.dump(comparison_data, f)
            
            with app.test_client() as client:
                with app.app_context():
                    yield client, comparison_data
    
    def test_save_selections(self, client_with_data):
        """Test saving selection updates"""
        client, original_data = client_with_data
        
        # Modify selections
        modified_data = original_data.copy()
        if modified_data['different_cards']:
            modified_data['different_cards'][0]['selected'] = 'file2'
        
        response = client.post('/save_selections', 
                             data=json.dumps(modified_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        
        # Verify data was saved
        data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
        with open(data_file, 'r') as f:
            saved_data = json.load(f)
        
        if saved_data['different_cards']:
            assert saved_data['different_cards'][0]['selected'] == 'file2'
    
    def test_save_invalid_data(self, client_with_data):
        """Test saving invalid JSON data"""
        client, _ = client_with_data
        
        response = client.post('/save_selections', 
                             data="invalid json",
                             content_type='application/json')
        
        # Should handle invalid JSON gracefully
        assert response.status_code in [400, 500]  # Either is acceptable

class TestExportGeneration:
    """Test export file generation"""
    
    @pytest.fixture
    def client_with_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            # Create test data
            dataset = TestFixtures.small_normal()
            comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
            
            data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
            with open(data_file, 'w') as f:
                json.dump(comparison_data, f)
            
            with app.test_client() as client:
                with app.app_context():
                    yield client
    
    def test_generate_export(self, client_with_data):
        """Test generating and downloading export file"""
        response = client_with_data.get('/generate_export')
        
        assert response.status_code == 200
        # Content type may vary - just check it's a download
        assert 'merged_anki_export.txt' in response.headers.get('Content-Disposition', '')
        
        # Verify content is valid Anki format
        content = response.data.decode('utf-8')
        lines = content.strip().split('\n')
        
        # Should have headers
        header_lines = [line for line in lines if line.startswith('#')]
        assert len(header_lines) > 0
        
        # Should have card data
        card_lines = [line for line in lines if '\t' in line and not line.startswith('#')]
        assert len(card_lines) > 0
        
        # Each card should have exactly one tab
        for line in card_lines:
            assert line.count('\t') == 1
    
    def test_generate_export_without_data(self):
        """Test generating export without existing data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            with app.test_client() as client:
                response = client.get('/generate_export')
                
                # Should redirect to index
                assert response.status_code == 302

class TestResetFunctionality:
    """Test reset and cleanup functionality"""
    
    @pytest.fixture
    def client_with_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            # Create test data and files
            dataset = TestFixtures.small_normal()
            comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
            
            data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
            with open(data_file, 'w') as f:
                json.dump(comparison_data, f)
            
            # Create some upload files
            upload_file = os.path.join(app.config['UPLOAD_FOLDER'], 'test.txt')
            with open(upload_file, 'w') as f:
                f.write('test content')
            
            with app.test_client() as client:
                with app.app_context():
                    yield client
    
    def test_reset(self, client_with_data):
        """Test reset functionality"""
        # Verify files exist before reset
        data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
        upload_file = os.path.join(app.config['UPLOAD_FOLDER'], 'test.txt')
        
        assert os.path.exists(data_file)
        assert os.path.exists(upload_file)
        
        response = client_with_data.get('/reset')
        
        # Should redirect to index
        assert response.status_code == 302
        assert '/' in response.headers['Location']
        
        # Files should be cleaned up
        assert not os.path.exists(data_file)
        assert not os.path.exists(upload_file)

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def client(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            with app.test_client() as client:
                with app.app_context():
                    yield client
    
    def test_upload_malformed_files(self, client):
        """Test handling of malformed Anki files"""
        malformed_content = "This is not a valid Anki export\nNo tabs here\nInvalid format"
        
        data = {
            'file1': (BytesIO(malformed_content.encode('utf-8')), 'malformed1.txt'),
            'file2': (BytesIO(malformed_content.encode('utf-8')), 'malformed2.txt'),
            'file1_name': 'Malformed File 1',
            'file2_name': 'Malformed File 2'
        }
        
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        
        # Should handle gracefully (either success with empty data or error)
        assert response.status_code in [200, 302, 400]
    
    def test_concurrent_access(self, client):
        """Test handling of concurrent access to data files"""
        # This is a basic test - full concurrency testing would require more setup
        dataset = TestFixtures.small_normal()
        comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
        
        # Simulate concurrent save operations
        for i in range(5):
            response = client.post('/save_selections',
                                 data=json.dumps(comparison_data),
                                 content_type='application/json')
            # Should handle concurrent saves gracefully
            assert response.status_code in [200, 500]  # Either success or handled error

if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v", "--tb=short"])