#!/usr/bin/env python3
"""
Performance and Load Tests for Anki Diff Tool
Tests application performance under various load conditions
"""

import pytest
import os
import sys
import time
import threading
import concurrent.futures
import psutil
import tempfile
import json
import requests
from typing import List, Dict, Tuple
import statistics

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.web_app import app, compare_exports, generate_anki_export
from tests.fixtures.test_data_factory import TestDataFactory, DatasetSize, ScenarioType

class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.peak_memory = None
        self.start_cpu = None
        self.cpu_readings = []
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.start_memory = psutil.virtual_memory().used
        self.start_cpu = psutil.cpu_percent()
        self.peak_memory = self.start_memory
        self.cpu_readings = []
        self.monitoring = True
        
        # Start background monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict:
        """Stop monitoring and return results"""
        self.monitoring = False
        self.end_time = time.time()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        current_memory = psutil.virtual_memory().used
        
        return {
            'duration': self.end_time - self.start_time,
            'memory_start_mb': self.start_memory / 1024 / 1024,
            'memory_peak_mb': self.peak_memory / 1024 / 1024,
            'memory_end_mb': current_memory / 1024 / 1024,
            'memory_used_mb': (self.peak_memory - self.start_memory) / 1024 / 1024,
            'cpu_avg_percent': statistics.mean(self.cpu_readings) if self.cpu_readings else 0,
            'cpu_peak_percent': max(self.cpu_readings) if self.cpu_readings else 0
        }
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            current_memory = psutil.virtual_memory().used
            self.peak_memory = max(self.peak_memory, current_memory)
            
            cpu_percent = psutil.cpu_percent()
            self.cpu_readings.append(cpu_percent)
            
            time.sleep(0.1)  # Monitor every 100ms

@pytest.mark.performance
class TestFileProcessingPerformance:
    """Test performance of core file processing functions"""
    
    def test_small_file_processing_performance(self):
        """Test processing performance with small files"""
        dataset = TestDataFactory.create_dataset(DatasetSize.SMALL)
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        monitor = PerformanceMonitor()
        
        try:
            monitor.start_monitoring()
            
            # Time the comparison operation
            start_time = time.time()
            result = compare_exports(file1_path, file2_path)
            comparison_time = time.time() - start_time
            
            perf_data = monitor.stop_monitoring()
            
            # Performance assertions
            assert comparison_time < 1.0, f"Small file comparison too slow: {comparison_time:.2f}s"
            assert perf_data['memory_used_mb'] < 50, f"Too much memory used: {perf_data['memory_used_mb']:.1f}MB"
            
            print(f"✅ Small file processing: {comparison_time:.3f}s, {perf_data['memory_used_mb']:.1f}MB")
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
    
    def test_medium_file_processing_performance(self):
        """Test processing performance with medium files"""
        dataset = TestDataFactory.create_dataset(DatasetSize.MEDIUM)
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        monitor = PerformanceMonitor()
        
        try:
            monitor.start_monitoring()
            
            start_time = time.time()
            result = compare_exports(file1_path, file2_path)
            comparison_time = time.time() - start_time
            
            perf_data = monitor.stop_monitoring()
            
            # Performance assertions for medium files
            assert comparison_time < 5.0, f"Medium file comparison too slow: {comparison_time:.2f}s"
            assert perf_data['memory_used_mb'] < 100, f"Too much memory used: {perf_data['memory_used_mb']:.1f}MB"
            
            print(f"✅ Medium file processing: {comparison_time:.3f}s, {perf_data['memory_used_mb']:.1f}MB")
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
    
    def test_large_file_processing_performance(self):
        """Test processing performance with large files"""
        dataset = TestDataFactory.create_dataset(DatasetSize.LARGE)
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        monitor = PerformanceMonitor()
        
        try:
            monitor.start_monitoring()
            
            start_time = time.time()
            result = compare_exports(file1_path, file2_path)
            comparison_time = time.time() - start_time
            
            perf_data = monitor.stop_monitoring()
            
            # Performance assertions for large files
            assert comparison_time < 30.0, f"Large file comparison too slow: {comparison_time:.2f}s"
            assert perf_data['memory_used_mb'] < 500, f"Too much memory used: {perf_data['memory_used_mb']:.1f}MB"
            
            print(f"✅ Large file processing: {comparison_time:.3f}s, {perf_data['memory_used_mb']:.1f}MB")
            
            # Additional checks for large files
            assert result['stats']['file1_total'] > 100, "Should have processed many cards"
            assert len(result['identical_cards']) + len(result['different_cards']) + len(result['unique_file1']) + len(result['unique_file2']) > 100
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
    
    def test_export_generation_performance(self):
        """Test export generation performance"""
        dataset = TestDataFactory.create_dataset(DatasetSize.MEDIUM)
        comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            output_path = f.name
        
        monitor = PerformanceMonitor()
        
        try:
            monitor.start_monitoring()
            
            start_time = time.time()
            generate_anki_export(comparison_data, output_path)
            export_time = time.time() - start_time
            
            perf_data = monitor.stop_monitoring()
            
            # Performance assertions
            assert export_time < 2.0, f"Export generation too slow: {export_time:.2f}s"
            assert perf_data['memory_used_mb'] < 100, f"Too much memory used: {perf_data['memory_used_mb']:.1f}MB"
            
            # Verify file was created
            assert os.path.exists(output_path)
            file_size = os.path.getsize(output_path)
            assert file_size > 0, "Generated file should not be empty"
            
            print(f"✅ Export generation: {export_time:.3f}s, {file_size} bytes, {perf_data['memory_used_mb']:.1f}MB")
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

@pytest.mark.performance
class TestConcurrentAccess:
    """Test performance under concurrent access"""
    
    @pytest.fixture
    def app_client(self):
        """Setup test client"""
        with tempfile.TemporaryDirectory() as temp_dir:
            app.config['TESTING'] = True
            app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
            app.config['DATA_FOLDER'] = os.path.join(temp_dir, 'data')
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
            
            with app.test_client() as client:
                yield client
    
    def test_concurrent_file_processing(self):
        """Test concurrent file processing operations"""
        num_concurrent = 5
        datasets = [TestDataFactory.create_dataset(DatasetSize.SMALL) for _ in range(num_concurrent)]
        
        def process_files(dataset_index):
            """Process files for a single dataset"""
            dataset = datasets[dataset_index]
            file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
            
            try:
                start_time = time.time()
                result = compare_exports(file1_path, file2_path)
                processing_time = time.time() - start_time
                
                return {
                    'index': dataset_index,
                    'time': processing_time,
                    'cards_processed': result['stats']['file1_total'] + result['stats']['file2_total'],
                    'success': True
                }
            except Exception as e:
                return {
                    'index': dataset_index,
                    'error': str(e),
                    'success': False
                }
            finally:
                try:
                    os.unlink(file1_path)
                    os.unlink(file2_path)
                except:
                    pass
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # Run concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(process_files, i) for i in range(num_concurrent)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        perf_data = monitor.stop_monitoring()
        
        # Verify all operations completed successfully
        successful_results = [r for r in results if r.get('success', False)]
        assert len(successful_results) == num_concurrent, f"Only {len(successful_results)}/{num_concurrent} operations succeeded"
        
        # Check performance metrics
        avg_time = statistics.mean([r['time'] for r in successful_results])
        max_time = max([r['time'] for r in successful_results])
        
        assert max_time < 10.0, f"Concurrent processing too slow: {max_time:.2f}s max"
        assert perf_data['memory_used_mb'] < 200, f"Too much memory used: {perf_data['memory_used_mb']:.1f}MB"
        
        print(f"✅ Concurrent processing: {num_concurrent} operations, avg: {avg_time:.3f}s, max: {max_time:.3f}s")
    
    def test_concurrent_api_requests(self, app_client):
        """Test concurrent API requests"""
        # Setup test data
        dataset = TestDataFactory.create_dataset(DatasetSize.SMALL)
        comparison_data = TestDataFactory.dataset_to_comparison_data(dataset)
        
        # Save initial data
        data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
        with open(data_file, 'w') as f:
            json.dump(comparison_data, f)
        
        num_concurrent = 10
        
        def make_api_request(request_index):
            """Make a single API request"""
            try:
                start_time = time.time()
                
                # Alternate between save and select requests
                if request_index % 2 == 0:
                    response = app_client.post('/save_selections',
                                            data=json.dumps(comparison_data),
                                            content_type='application/json')
                else:
                    response = app_client.get('/select')
                
                request_time = time.time() - start_time
                
                return {
                    'index': request_index,
                    'time': request_time,
                    'status_code': response.status_code,
                    'success': response.status_code in [200, 302]
                }
            except Exception as e:
                return {
                    'index': request_index,
                    'error': str(e),
                    'success': False
                }
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # Run concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_api_request, i) for i in range(num_concurrent)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        perf_data = monitor.stop_monitoring()
        
        # Verify results
        successful_results = [r for r in results if r.get('success', False)]
        assert len(successful_results) >= num_concurrent * 0.8, f"Too many failed requests: {len(successful_results)}/{num_concurrent}"
        
        # Performance checks
        avg_time = statistics.mean([r['time'] for r in successful_results])
        max_time = max([r['time'] for r in successful_results])
        
        assert max_time < 5.0, f"API requests too slow: {max_time:.2f}s max"
        assert avg_time < 1.0, f"API requests too slow on average: {avg_time:.2f}s avg"
        
        print(f"✅ Concurrent API: {len(successful_results)}/{num_concurrent} successful, avg: {avg_time:.3f}s")

@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage patterns"""
    
    def test_memory_efficiency_small_files(self):
        """Test memory efficiency with small files"""
        dataset = TestDataFactory.create_dataset(DatasetSize.SMALL)
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        try:
            initial_memory = psutil.virtual_memory().used
            
            # Process files multiple times to check for memory leaks
            for i in range(10):
                result = compare_exports(file1_path, file2_path)
                
                current_memory = psutil.virtual_memory().used
                memory_increase = (current_memory - initial_memory) / 1024 / 1024
                
                # Memory should not continuously increase (indicating leaks)
                assert memory_increase < 100, f"Possible memory leak: {memory_increase:.1f}MB increase after {i+1} iterations"
            
            print("✅ No memory leaks detected in small file processing")
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)
    
    def test_memory_cleanup_large_files(self):
        """Test memory cleanup after processing large files"""
        dataset = TestDataFactory.create_dataset(DatasetSize.LARGE)
        file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
        
        try:
            initial_memory = psutil.virtual_memory().used
            
            # Process large files
            result = compare_exports(file1_path, file2_path)
            
            peak_memory = psutil.virtual_memory().used
            memory_used = (peak_memory - initial_memory) / 1024 / 1024
            
            # Delete result to encourage garbage collection
            del result
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Wait a bit for cleanup
            time.sleep(1)
            
            final_memory = psutil.virtual_memory().used
            memory_remaining = (final_memory - initial_memory) / 1024 / 1024
            
            # Most memory should be cleaned up
            cleanup_ratio = (memory_used - memory_remaining) / memory_used if memory_used > 0 else 1
            
            assert cleanup_ratio > 0.7, f"Poor memory cleanup: only {cleanup_ratio:.1%} cleaned up"
            
            print(f"✅ Memory cleanup: {memory_used:.1f}MB used, {cleanup_ratio:.1%} cleaned up")
            
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)

@pytest.mark.performance
class TestScalabilityLimits:
    """Test scalability limits and breaking points"""
    
    def test_maximum_file_size_handling(self):
        """Test handling of very large files"""
        # Create a very large dataset
        try:
            dataset = TestDataFactory.create_dataset(DatasetSize.LARGE)
            
            # Multiply the dataset to make it even larger
            for _ in range(5):  # 5x larger
                dataset.identical_cards.extend(dataset.identical_cards.copy())
                dataset.different_cards.extend(dataset.different_cards.copy())
                dataset.unique_file1.extend(dataset.unique_file1.copy())
                dataset.unique_file2.extend(dataset.unique_file2.copy())
            
            file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
            
            # Check file sizes
            file1_size = os.path.getsize(file1_path) / 1024 / 1024  # MB
            file2_size = os.path.getsize(file2_path) / 1024 / 1024  # MB
            
            print(f"Testing with files: {file1_size:.1f}MB and {file2_size:.1f}MB")
            
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            start_time = time.time()
            result = compare_exports(file1_path, file2_path)
            processing_time = time.time() - start_time
            
            perf_data = monitor.stop_monitoring()
            
            # Should complete within reasonable time and memory
            assert processing_time < 120.0, f"Very large file processing too slow: {processing_time:.2f}s"
            assert perf_data['memory_used_mb'] < 1000, f"Too much memory used: {perf_data['memory_used_mb']:.1f}MB"
            
            total_cards = result['stats']['file1_total'] + result['stats']['file2_total']
            cards_per_second = total_cards / processing_time
            
            print(f"✅ Large scale: {total_cards} cards, {processing_time:.1f}s, {cards_per_second:.0f} cards/s")
            
        except MemoryError:
            pytest.skip("Insufficient memory for maximum file size test")
        except Exception as e:
            if "memory" in str(e).lower():
                pytest.skip(f"Memory limitation reached: {e}")
            else:
                raise
        finally:
            try:
                os.unlink(file1_path)
                os.unlink(file2_path)
            except:
                pass
    
    def test_concurrent_user_simulation(self):
        """Simulate multiple concurrent users"""
        num_users = 20
        operations_per_user = 3
        
        def simulate_user(user_id):
            """Simulate a single user's operations"""
            operations = []
            
            for op_id in range(operations_per_user):
                try:
                    # Create small dataset for this operation
                    dataset = TestDataFactory.create_dataset(DatasetSize.TINY)
                    file1_path, file2_path = TestDataFactory.create_temp_files(dataset)
                    
                    start_time = time.time()
                    result = compare_exports(file1_path, file2_path)
                    operation_time = time.time() - start_time
                    
                    operations.append({
                        'user_id': user_id,
                        'operation_id': op_id,
                        'time': operation_time,
                        'success': True
                    })
                    
                    os.unlink(file1_path)
                    os.unlink(file2_path)
                    
                except Exception as e:
                    operations.append({
                        'user_id': user_id,
                        'operation_id': op_id,
                        'error': str(e),
                        'success': False
                    })
            
            return operations
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # Simulate concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(simulate_user, i) for i in range(num_users)]
            all_operations = []
            for future in concurrent.futures.as_completed(futures):
                all_operations.extend(future.result())
        
        perf_data = monitor.stop_monitoring()
        
        # Analyze results
        successful_ops = [op for op in all_operations if op.get('success', False)]
        success_rate = len(successful_ops) / len(all_operations)
        
        assert success_rate > 0.9, f"Low success rate under load: {success_rate:.1%}"
        
        if successful_ops:
            avg_time = statistics.mean([op['time'] for op in successful_ops])
            max_time = max([op['time'] for op in successful_ops])
            
            assert avg_time < 2.0, f"Operations too slow under load: {avg_time:.2f}s avg"
            assert max_time < 10.0, f"Some operations too slow: {max_time:.2f}s max"
        
        total_operations = len(all_operations)
        throughput = total_operations / perf_data['duration']
        
        print(f"✅ Concurrent load: {num_users} users, {success_rate:.1%} success, {throughput:.1f} ops/s")

if __name__ == "__main__":
    # Run performance tests if called directly
    pytest.main([__file__, "-v", "-m", "performance", "--tb=short"])