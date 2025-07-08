#!/usr/bin/env python3
"""
Manual Test Script for Anki Diff UI
Tests the UI functionality without requiring browser automation
"""

import sys
import os
import json
import time
import requests
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ManualUITester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_app_availability(self):
        """Test if the Flask app is running and accessible"""
        print("🔍 Testing Flask app availability...")
        
        try:
            response = self.session.get(self.base_url, timeout=5)
            if response.status_code in [200, 302]:  # 302 is redirect, which is fine
                print("✅ Flask app is running and accessible")
                return True
            else:
                print(f"⚠️ Flask app returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Flask app")
            print("💡 Make sure to run 'python app.py' first")
            return False
        except Exception as e:
            print(f"❌ Error testing app availability: {e}")
            return False
    
    def test_route_accessibility(self, route, route_name):
        """Test if a specific route is accessible"""
        print(f"🔍 Testing {route_name} ({route})...")
        
        try:
            response = self.session.get(urljoin(self.base_url, route), timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {route_name} accessible")
                
                # Check for basic HTML structure
                html = response.text
                if '<html' in html and '<body' in html:
                    print(f"  ✅ Valid HTML structure")
                else:
                    print(f"  ⚠️ HTML structure seems incomplete")
                    return False
                
                # Check for specific UI elements
                if route == '/select-new':
                    return self.analyze_new_ui_html(html)
                elif route == '/select':
                    return self.analyze_old_ui_html(html)
                
                return True
                
            elif response.status_code == 302:
                print(f"⚠️ {route_name} redirected (probably needs data)")
                return True
            else:
                print(f"❌ {route_name} returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing {route_name}: {e}")
            return False
    
    def analyze_new_ui_html(self, html):
        """Analyze the new UI HTML for expected elements"""
        print("  🔍 Analyzing new UI HTML structure...")
        
        checks = [
            ('🐛 Debug button', 'id="toggle-debug"'),
            ('📟 Console button', 'id="toggle-console"'),
            ('🧪 Test button', 'id="test-tabs"'),
            ('🔄 Different tab', 'id="different-tab"'),
            ('✅ Identical tab', 'id="identical-tab"'),
            ('📁 Unique1 tab', 'id="unique1-tab"'),
            ('📁 Unique2 tab', 'id="unique2-tab"'),
            ('Debug panel', 'id="debug-panel"'),
            ('Debug console', 'id="debug-console"'),
            ('AnkiDiffUI class', 'class AnkiDiffUI'),
            ('DebugLogger class', 'class DebugLogger'),
        ]
        
        all_good = True
        for check_name, check_pattern in checks:
            if check_pattern in html:
                print(f"    ✅ {check_name} found")
            else:
                print(f"    ❌ {check_name} missing")
                all_good = False
        
        # Check for card containers
        card_containers = [
            'different-cards-container',
            'identical-cards-container', 
            'unique1-cards-container',
            'unique2-cards-container'
        ]
        
        for container in card_containers:
            if f'id="{container}"' in html:
                print(f"    ✅ {container} found")
            else:
                print(f"    ❌ {container} missing")
                all_good = False
        
        return all_good
    
    def analyze_old_ui_html(self, html):
        """Analyze the old UI HTML for comparison"""
        print("  🔍 Analyzing old UI HTML structure...")
        
        checks = [
            ('Different tab', 'id="different-tab"'),
            ('Identical tab', 'id="identical-tab"'),
            ('Unique1 tab', 'id="unique1-tab"'),
            ('Unique2 tab', 'id="unique2-tab"'),
            ('Bootstrap tabs', 'data-bs-toggle="tab"'),
        ]
        
        all_good = True
        for check_name, check_pattern in checks:
            if check_pattern in html:
                print(f"    ✅ {check_name} found")
            else:
                print(f"    ❌ {check_name} missing")
                all_good = False
        
        return all_good
    
    def test_data_structure(self):
        """Test if the test data is properly structured"""
        print("🔍 Testing data structure...")
        
        try:
            data_file = os.path.join(os.path.dirname(__file__), 'src', 'data', 'comparison_data.json')
            
            if not os.path.exists(data_file):
                print("❌ comparison_data.json not found")
                return False
            
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            required_keys = ['stats', 'identical_cards', 'different_cards', 'unique_file1', 'unique_file2']
            
            for key in required_keys:
                if key in data:
                    print(f"    ✅ {key} present")
                else:
                    print(f"    ❌ {key} missing")
                    return False
            
            # Check stats
            stats = data['stats']
            print(f"    📊 Data counts:")
            print(f"      - Identical: {stats.get('identical', 0)}")
            print(f"      - Different: {stats.get('different', 0)}")
            print(f"      - Unique File1: {stats.get('only_file1', 0)}")
            print(f"      - Unique File2: {stats.get('only_file2', 0)}")
            
            # Verify counts match actual data
            actual_counts = {
                'identical': len(data.get('identical_cards', [])),
                'different': len(data.get('different_cards', [])),
                'only_file1': len(data.get('unique_file1', [])),
                'only_file2': len(data.get('unique_file2', []))
            }
            
            counts_match = True
            for key, actual in actual_counts.items():
                expected = stats.get(key, 0)
                if actual == expected:
                    print(f"    ✅ {key}: stats ({expected}) match actual ({actual})")
                else:
                    print(f"    ❌ {key}: stats ({expected}) != actual ({actual})")
                    counts_match = False
            
            return counts_match
            
        except Exception as e:
            print(f"❌ Error testing data structure: {e}")
            return False
    
    def run_manual_tests(self):
        """Run all manual tests"""
        print("🚀 Starting Manual UI Test Suite")
        print("=" * 60)
        
        results = []
        
        # Test 1: App availability
        results.append(("App Availability", self.test_app_availability()))
        
        # Test 2: Data structure
        results.append(("Data Structure", self.test_data_structure()))
        
        # Test 3: Old UI route
        results.append(("Old UI Route", self.test_route_accessibility("/select", "Old UI")))
        
        # Test 4: New UI route
        results.append(("New UI Route", self.test_route_accessibility("/select-new", "New UI")))
        
        # Test 5: API endpoints
        results.append(("Save Selections API", self.test_api_endpoint("/save_selections")))
        results.append(("Generate Export API", self.test_api_endpoint("/generate_export")))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name:<25} {status}")
            if result:
                passed += 1
        
        print(f"\n🏁 Tests completed: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All tests passed! The UI should be working correctly.")
            print("\n💡 Next steps:")
            print("  1. Open http://127.0.0.1:5000/select-new in your browser")
            print("  2. Click the '🐛 Debug' button to enable debug mode")
            print("  3. Click the '📟 Console' button to see detailed logging")
            print("  4. Click the '🧪 Test' button to run automated tab tests")
            print("  5. Try switching between all four tabs")
        else:
            print("❌ Some tests failed. Check the output above for details.")
        
        return passed == total
    
    def test_api_endpoint(self, endpoint):
        """Test if API endpoints are accessible (expecting POST for most)"""
        print(f"🔍 Testing API endpoint {endpoint}...")
        
        try:
            # For most API endpoints, we expect a method not allowed for GET
            response = self.session.get(urljoin(self.base_url, endpoint), timeout=5)
            
            if response.status_code == 405:  # Method not allowed - this is expected for POST endpoints
                print(f"  ✅ {endpoint} endpoint exists (method not allowed for GET, as expected)")
                return True
            elif response.status_code == 302:  # Redirect
                print(f"  ✅ {endpoint} endpoint accessible (redirected)")
                return True
            elif response.status_code == 200:  # OK
                print(f"  ✅ {endpoint} endpoint accessible")
                return True
            else:
                print(f"  ⚠️ {endpoint} returned unexpected status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error testing {endpoint}: {e}")
            return False

def main():
    """Main function"""
    print("🧪 Anki Diff UI Manual Testing Tool")
    print("This tool tests the UI without requiring browser automation")
    print()
    
    tester = ManualUITester()
    success = tester.run_manual_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())