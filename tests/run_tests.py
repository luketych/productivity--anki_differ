#!/usr/bin/env python3
"""
Comprehensive Test Runner for Anki Diff Tool
Provides different test execution modes and reporting
"""

import os
import sys
import subprocess
import argparse
import time
import json
from typing import Dict, List, Optional

class TestRunner:
    """Main test runner class"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.test_results = {}
        
    def run_unit_tests(self, verbose: bool = False) -> Dict:
        """Run unit tests"""
        print("🧪 Running Unit Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/unit/",
            "-m", "unit",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time
        
        return {
            'type': 'unit',
            'duration': duration,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'passed': result.returncode == 0
        }
    
    def run_integration_tests(self, verbose: bool = False) -> Dict:
        """Run integration tests"""
        print("🔗 Running Integration Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/integration/",
            "-m", "integration",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time
        
        return {
            'type': 'integration',
            'duration': duration,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'passed': result.returncode == 0
        }
    
    def run_e2e_tests(self, verbose: bool = False, headless: bool = True) -> Dict:
        """Run end-to-end tests"""
        print("🌐 Running End-to-End Tests...")
        
        # Check if Flask app is running
        if not self._check_flask_app():
            print("⚠️ Flask app not running. Starting it...")
            if not self._start_flask_app():
                return {
                    'type': 'e2e',
                    'duration': 0,
                    'returncode': 1,
                    'stdout': '',
                    'stderr': 'Flask app failed to start',
                    'passed': False
                }
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/e2e/",
            "-m", "e2e",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        if not headless:
            # Set environment variable for visible browser
            os.environ['E2E_HEADLESS'] = 'false'
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time
        
        return {
            'type': 'e2e',
            'duration': duration,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'passed': result.returncode == 0
        }
    
    def run_performance_tests(self, verbose: bool = False) -> Dict:
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/performance/",
            "-m", "performance",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time
        
        return {
            'type': 'performance',
            'duration': duration,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'passed': result.returncode == 0
        }
    
    def run_all_tests(self, verbose: bool = False, skip_slow: bool = False) -> Dict:
        """Run all test suites"""
        print("🚀 Running All Tests...")
        
        results = {}
        
        # Run unit tests (always fast)
        results['unit'] = self.run_unit_tests(verbose)
        
        # Run integration tests
        results['integration'] = self.run_integration_tests(verbose)
        
        if not skip_slow:
            # Run E2E tests (slow)
            results['e2e'] = self.run_e2e_tests(verbose, headless=True)
            
            # Run performance tests (slow)
            results['performance'] = self.run_performance_tests(verbose)
        else:
            print("⏭️ Skipping slow tests (E2E and Performance)")
        
        return results
    
    def run_smoke_tests(self, verbose: bool = False) -> Dict:
        """Run quick smoke tests for CI/CD"""
        print("💨 Running Smoke Tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/unit/test_core_functions.py::TestLoadAnkiExport::test_load_valid_file",
            "tests/unit/test_core_functions.py::TestCompareExports::test_compare_different_files",
            "tests/integration/test_api_endpoints.py::TestIndexRoute::test_index_without_data",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time
        
        return {
            'type': 'smoke',
            'duration': duration,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'passed': result.returncode == 0
        }
    
    def run_coverage_tests(self, verbose: bool = False) -> Dict:
        """Run tests with coverage analysis"""
        print("📊 Running Tests with Coverage Analysis...")
        
        try:
            import coverage
        except ImportError:
            print("❌ Coverage package not installed. Install with: pip install coverage")
            return {
                'type': 'coverage',
                'duration': 0,
                'returncode': 1,
                'stdout': '',
                'stderr': 'Coverage package not available',
                'passed': False
            }
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/unit/",
            "tests/integration/",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term",
            "--cov-fail-under=70",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time
        
        return {
            'type': 'coverage',
            'duration': duration,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'passed': result.returncode == 0
        }
    
    def _check_flask_app(self) -> bool:
        """Check if Flask app is running"""
        try:
            import requests
            response = requests.get("http://127.0.0.1:5000", timeout=2)
            return response.status_code in [200, 302]
        except:
            return False
    
    def _start_flask_app(self) -> bool:
        """Attempt to start Flask app"""
        print("🚀 Starting Flask app for E2E tests...")
        
        # This is a simplified version - in practice you'd use subprocess
        # and manage the Flask app lifecycle properly
        try:
            # Check if virtual environment is active and has Flask
            result = subprocess.run([
                sys.executable, "-c", "import flask; print('Flask available')"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Flask is available")
                print("💡 Please start the Flask app manually: python app.py")
                return True
            else:
                print("❌ Flask not available")
                return False
        except Exception as e:
            print(f"❌ Error checking Flask: {e}")
            return False
    
    def print_results(self, results: Dict):
        """Print formatted test results"""
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        if isinstance(results, dict) and 'type' in results:
            # Single test result
            results = {results['type']: results}
        
        total_duration = 0
        passed_suites = 0
        total_suites = len(results)
        
        for suite_name, result in results.items():
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            duration = result['duration']
            total_duration += duration
            
            if result['passed']:
                passed_suites += 1
            
            print(f"  {suite_name.upper():<15} {status:<10} ({duration:.2f}s)")
            
            # Show errors if any
            if not result['passed'] and result['stderr']:
                print(f"    Error: {result['stderr'][:100]}...")
        
        print("-" * 60)
        print(f"  {'TOTAL':<15} {passed_suites}/{total_suites} passed ({total_duration:.2f}s)")
        
        if passed_suites == total_suites:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️ {total_suites - passed_suites} test suite(s) failed")
        
        print("=" * 60)
    
    def save_results(self, results: Dict, filename: str = "test_results.json"):
        """Save test results to JSON file"""
        results_file = os.path.join(self.project_root, filename)
        
        # Add metadata
        results_with_meta = {
            'timestamp': time.time(),
            'project_root': self.project_root,
            'python_version': sys.version,
            'results': results
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_with_meta, f, indent=2)
        
        print(f"📁 Results saved to {results_file}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Anki Diff Tool Test Runner')
    
    parser.add_argument('mode', nargs='?', default='all',
                       choices=['unit', 'integration', 'e2e', 'performance', 'all', 'smoke', 'coverage'],
                       help='Test mode to run (default: all)')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    parser.add_argument('--skip-slow', action='store_true',
                       help='Skip slow tests (E2E and Performance)')
    
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run E2E tests in headless mode (default: True)')
    
    parser.add_argument('--save-results', metavar='FILE',
                       help='Save results to JSON file')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    print("🧪 Anki Diff Tool Test Runner")
    print("=" * 40)
    
    # Run tests based on mode
    if args.mode == 'unit':
        results = runner.run_unit_tests(args.verbose)
    elif args.mode == 'integration':
        results = runner.run_integration_tests(args.verbose)
    elif args.mode == 'e2e':
        results = runner.run_e2e_tests(args.verbose, args.headless)
    elif args.mode == 'performance':
        results = runner.run_performance_tests(args.verbose)
    elif args.mode == 'smoke':
        results = runner.run_smoke_tests(args.verbose)
    elif args.mode == 'coverage':
        results = runner.run_coverage_tests(args.verbose)
    elif args.mode == 'all':
        results = runner.run_all_tests(args.verbose, args.skip_slow)
    
    # Print results
    runner.print_results(results)
    
    # Save results if requested
    if args.save_results:
        runner.save_results(results, args.save_results)
    
    # Exit with appropriate code
    if isinstance(results, dict):
        if 'passed' in results:
            # Single test result
            exit_code = 0 if results['passed'] else 1
        else:
            # Multiple test results
            exit_code = 0 if all(r['passed'] for r in results.values()) else 1
    else:
        exit_code = 1
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()