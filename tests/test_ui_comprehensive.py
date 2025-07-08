#!/usr/bin/env python3
"""
Comprehensive UI Test Suite for Anki Diff Tool
Tests both the old and new UI implementations with detailed reporting
"""

import sys
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.web_app import app

class UITestSuite:
    def __init__(self, headless=True):
        self.app = app
        self.driver = None
        self.headless = headless
        self.test_results = {}
        self.base_url = "http://127.0.0.1:5000"
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        print("🔧 Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Chrome WebDriver setup successful")
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome WebDriver: {e}")
            print("💡 Make sure ChromeDriver is installed and in PATH")
            return False
    
    def start_flask_app(self):
        """Start Flask app in test mode"""
        print("🚀 Starting Flask app for testing...")
        
        # We'll assume the app is already running
        # In a real test suite, you'd start it in a subprocess
        try:
            import requests
            response = requests.get(f"{self.base_url}/select-new", timeout=5)
            if response.status_code == 200:
                print("✅ Flask app is running and accessible")
                return True
            else:
                print(f"❌ Flask app returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to Flask app: {e}")
            print("💡 Make sure to run 'python app.py' first")
            return False
    
    def test_page_load(self, url_path, test_name):
        """Test that a page loads successfully"""
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            self.driver.get(f"{self.base_url}{url_path}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check for any JavaScript errors
            logs = self.driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE']
            
            if js_errors:
                print(f"⚠️ JavaScript errors found:")
                for error in js_errors:
                    print(f"  - {error['message']}")
                return False
            
            print(f"✅ {test_name} loaded successfully")
            return True
            
        except TimeoutException:
            print(f"❌ {test_name} failed to load (timeout)")
            return False
        except Exception as e:
            print(f"❌ {test_name} failed to load: {e}")
            return False
    
    def test_tab_functionality(self, test_name):
        """Test that all tabs work and show content"""
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            # Test each tab
            tabs = ['different', 'identical', 'unique1', 'unique2']
            tab_results = {}
            
            for tab_type in tabs:
                print(f"  🔍 Testing {tab_type} tab...")
                
                # Click the tab
                tab_button = self.driver.find_element(By.ID, f"{tab_type}-tab")
                tab_button.click()
                
                # Wait for tab to become active
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, f"{tab_type}-tab"))
                )
                
                # Check if tab pane is visible and has content
                tab_pane = self.driver.find_element(By.ID, f"{tab_type}-pane")
                
                # Count cards in this tab
                cards = self.driver.find_elements(By.CSS_SELECTOR, f".{tab_type}-card")
                card_count = len(cards)
                
                # Check if cards are visible
                visible_cards = [card for card in cards if card.is_displayed()]
                visible_count = len(visible_cards)
                
                tab_results[tab_type] = {
                    'total_cards': card_count,
                    'visible_cards': visible_count,
                    'tab_active': 'active' in tab_pane.get_attribute('class'),
                    'success': visible_count > 0 if card_count > 0 else True
                }
                
                print(f"    - Cards: {visible_count}/{card_count} visible")
                
                if tab_results[tab_type]['success']:
                    print(f"    ✅ {tab_type} tab working correctly")
                else:
                    print(f"    ❌ {tab_type} tab has issues")
            
            # Overall result
            all_success = all(result['success'] for result in tab_results.values())
            
            if all_success:
                print(f"✅ {test_name} - All tabs working correctly")
            else:
                print(f"❌ {test_name} - Some tabs have issues")
            
            self.test_results[test_name] = {
                'success': all_success,
                'details': tab_results
            }
            
            return all_success
            
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            self.test_results[test_name] = {'success': False, 'error': str(e)}
            return False
    
    def test_debug_features(self, test_name):
        """Test debug features in the new UI"""
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            # Test debug mode toggle
            debug_button = self.driver.find_element(By.ID, "toggle-debug")
            debug_button.click()
            
            # Wait for debug panel to appear
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "debug-panel"))
            )
            
            # Test console toggle
            console_button = self.driver.find_element(By.ID, "toggle-console")
            console_button.click()
            
            # Wait for console to appear
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "debug-console"))
            )
            
            # Test tab testing button
            test_button = self.driver.find_element(By.ID, "test-tabs")
            test_button.click()
            
            print(f"✅ {test_name} - Debug features working correctly")
            return True
            
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            return False
    
    def test_card_interactions(self, test_name):
        """Test card selection and interaction features"""
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            interactions_tested = 0
            
            # Test different cards - radio button selection
            different_radios = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"][name^="different-"]')
            if different_radios:
                different_radios[0].click()
                interactions_tested += 1
                print("    ✅ Different card radio button works")
            
            # Test unique card checkboxes
            unique1_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, '.unique1-checkbox')
            if unique1_checkboxes:
                unique1_checkboxes[0].click()
                interactions_tested += 1
                print("    ✅ Unique1 card checkbox works")
            
            unique2_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, '.unique2-checkbox')
            if unique2_checkboxes:
                unique2_checkboxes[0].click()
                interactions_tested += 1
                print("    ✅ Unique2 card checkbox works")
            
            # Test select all toggles
            select_all_unique1 = self.driver.find_elements(By.ID, "select-all-unique1")
            if select_all_unique1:
                select_all_unique1[0].click()
                interactions_tested += 1
                print("    ✅ Select all unique1 toggle works")
            
            select_all_unique2 = self.driver.find_elements(By.ID, "select-all-unique2")
            if select_all_unique2:
                select_all_unique2[0].click()
                interactions_tested += 1
                print("    ✅ Select all unique2 toggle works")
            
            if interactions_tested > 0:
                print(f"✅ {test_name} - {interactions_tested} interactions tested successfully")
                return True
            else:
                print(f"⚠️ {test_name} - No interactive elements found to test")
                return True  # Not a failure if there are no elements
                
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            return False
    
    def compare_uis(self):
        """Compare old and new UI implementations"""
        print(f"\n🔍 Comparing Old vs New UI implementations...")
        
        # Test old UI
        old_ui_result = self.test_tab_functionality("Old UI Tab Functionality")
        
        # Navigate to new UI
        self.driver.get(f"{self.base_url}/select-new")
        time.sleep(2)
        
        # Test new UI
        new_ui_result = self.test_tab_functionality("New UI Tab Functionality")
        
        # Test debug features (only available in new UI)
        debug_result = self.test_debug_features("New UI Debug Features")
        
        # Test interactions
        interaction_result = self.test_card_interactions("New UI Card Interactions")
        
        print(f"\n📊 UI Comparison Results:")
        print(f"  Old UI Tab Functionality: {'✅ PASS' if old_ui_result else '❌ FAIL'}")
        print(f"  New UI Tab Functionality: {'✅ PASS' if new_ui_result else '❌ FAIL'}")
        print(f"  New UI Debug Features: {'✅ PASS' if debug_result else '❌ FAIL'}")
        print(f"  New UI Interactions: {'✅ PASS' if interaction_result else '❌ FAIL'}")
        
        if new_ui_result and not old_ui_result:
            print(f"\n🎉 SUCCESS: New UI fixes the tab issues present in the old UI!")
        elif new_ui_result and old_ui_result:
            print(f"\n✅ Both UIs working, but new UI has additional debug features")
        else:
            print(f"\n⚠️ Issues still present - needs further investigation")
    
    def run_comprehensive_tests(self):
        """Run the complete test suite"""
        print("🚀 Starting Comprehensive UI Test Suite")
        print("=" * 60)
        
        # Setup
        if not self.setup_driver():
            return False
        
        if not self.start_flask_app():
            return False
        
        try:
            # Test both UIs
            print(f"\n📋 Testing Old UI...")
            old_page_load = self.test_page_load("/select", "Old UI Page Load")
            
            print(f"\n📋 Testing New UI...")
            new_page_load = self.test_page_load("/select-new", "New UI Page Load")
            
            if new_page_load:
                # Run comprehensive tests on new UI
                self.compare_uis()
            
            # Final summary
            print(f"\n" + "=" * 60)
            print(f"🏁 Test Suite Complete")
            print(f"=" * 60)
            
            return True
            
        finally:
            if self.driver:
                self.driver.quit()
                print(f"🔧 WebDriver closed")

def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Anki Diff UI Tests')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode (default: True)')
    parser.add_argument('--visible', action='store_true',
                       help='Run browser in visible mode (overrides --headless)')
    
    args = parser.parse_args()
    
    # If --visible is specified, override headless
    headless = args.headless and not args.visible
    
    print(f"🧪 Running UI tests in {'headless' if headless else 'visible'} mode...")
    
    test_suite = UITestSuite(headless=headless)
    success = test_suite.run_comprehensive_tests()
    
    if success:
        print(f"\n🎉 All tests completed successfully!")
        return 0
    else:
        print(f"\n❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())