#!/usr/bin/env python3
"""
Demo Script - Comprehensive Testing Strategy
Demonstrates all testing capabilities of the Anki Diff Tool
"""

import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """Run a command and show results"""
    print(f"\n{'='*60}")
    print(f"🎯 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    start_time = time.time()
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    duration = time.time() - start_time
    
    print(f"\n⏱️ Completed in {duration:.2f}s")
    print(f"🔢 Exit code: {result.returncode}")
    
    return result.returncode == 0

def main():
    print("🧪 Anki Diff Tool - Comprehensive Testing Strategy Demo")
    print("🎯 This demo showcases our complete testing framework")
    print()
    
    # Activate virtual environment
    venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
    if not os.path.exists(venv_python):
        venv_python = 'python'  # Fallback to system python
    
    success_count = 0
    total_tests = 0
    
    # 1. Demo Test Data Factory
    total_tests += 1
    print(f"\n🏭 Test Data Factory Demo")
    print("Generating various test datasets...")
    success = run_command([venv_python, 'tests/fixtures/test_data_factory.py'], 
                         "Test Data Factory - Generate Sample Datasets")
    if success:
        success_count += 1
    
    # 2. Run Smoke Tests (fastest)
    total_tests += 1
    success = run_command([venv_python, 'run_tests.py', 'smoke'], 
                         "Smoke Tests - Quick Validation")
    if success:
        success_count += 1
    
    # 3. Run Unit Tests
    total_tests += 1
    success = run_command([venv_python, 'run_tests.py', 'unit'], 
                         "Unit Tests - Core Function Testing")
    if success:
        success_count += 1
    
    # 4. Run Integration Tests
    total_tests += 1
    success = run_command([venv_python, 'run_tests.py', 'integration'], 
                         "Integration Tests - API Endpoint Testing")
    if success:
        success_count += 1
    
    # 5. Demo Manual Testing (without browser)
    total_tests += 1
    success = run_command([venv_python, 'test_manual.py'], 
                         "Manual Tests - UI Structure Validation")
    if success:
        success_count += 1
    
    # 6. Coverage Analysis (if pytest-cov is available)
    total_tests += 1
    try:
        import coverage
        success = run_command([venv_python, 'run_tests.py', 'coverage'], 
                             "Coverage Analysis - Code Coverage Report")
        if success:
            success_count += 1
    except ImportError:
        print(f"\n⚠️ Coverage testing skipped (pytest-cov not installed)")
        total_tests -= 1
    
    # 7. Performance Tests Demo (basic)
    total_tests += 1
    print(f"\n⚡ Performance Testing Demo")
    print("Note: Full performance tests require more resources")
    success = run_command([venv_python, '-c', '''
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from tests.fixtures.test_data_factory import TestDataFactory, DatasetSize
from src.web_app import compare_exports
import time

print("🔍 Testing small dataset performance...")
dataset = TestDataFactory.create_dataset(DatasetSize.SMALL)
file1_path, file2_path = TestDataFactory.create_temp_files(dataset)

try:
    start_time = time.time()
    result = compare_exports(file1_path, file2_path)
    duration = time.time() - start_time
    
    print(f"✅ Processed {result['stats']['file1_total'] + result['stats']['file2_total']} cards in {duration:.3f}s")
    print(f"📊 Found: {result['stats']['identical']} identical, {result['stats']['different']} different")
    print(f"📊 Unique: {result['stats']['only_file1']} + {result['stats']['only_file2']} unique cards")
finally:
    import os
    os.unlink(file1_path)
    os.unlink(file2_path)
'''], "Performance Test Demo - Small Dataset Processing")
    if success:
        success_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 TESTING STRATEGY DEMO SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {success_count}/{total_tests}")
    print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print(f"\n🎉 All test categories completed successfully!")
        print(f"\n📋 Available Test Commands:")
        print(f"  python run_tests.py smoke      # Quick validation")
        print(f"  python run_tests.py unit       # Unit tests")
        print(f"  python run_tests.py integration # API tests")
        print(f"  python run_tests.py e2e        # End-to-end tests (requires browser)")
        print(f"  python run_tests.py performance # Performance tests")
        print(f"  python run_tests.py all        # All tests")
        print(f"  python run_tests.py coverage   # Coverage analysis")
        
        print(f"\n🏗️ Test Architecture:")
        print(f"  📁 tests/fixtures/     - Test data factory and mock data")
        print(f"  📁 tests/unit/         - Unit tests (fast, isolated)")
        print(f"  📁 tests/integration/  - Integration tests (API, file I/O)")
        print(f"  📁 tests/e2e/          - End-to-end tests (browser, workflows)")
        print(f"  📁 tests/performance/  - Performance and load tests")
        
        print(f"\n🎯 Testing Strategy Benefits:")
        print(f"  🔧 Comprehensive coverage from unit to E2E")
        print(f"  🚀 Fast feedback with different test tiers")
        print(f"  🔍 Detailed debugging with extensive logging")
        print(f"  📊 Performance monitoring and benchmarking")
        print(f"  🏭 Consistent test data generation")
        print(f"  🤖 Automated CI/CD ready test pipeline")
        
    else:
        print(f"\n⚠️ Some test categories failed. Check output above for details.")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)