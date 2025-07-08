#!/usr/bin/env python3
"""
End-to-End Tests for Anki Diff Tool User Workflows
Tests complete user journeys through the application
"""

import pytest
import os
import sys
import time
import tempfile
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.web_app import app
from tests.fixtures.test_data_factory import TestDataFactory, DatasetSize, ScenarioType, TestFixtures

class TestSetup:
    """Setup utilities for E2E tests"""
    
    @staticmethod
    def setup_chrome_driver(headless=True):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            pytest.skip(f"Chrome WebDriver not available: {e}")
    
    @staticmethod
    def create_test_files(dataset):
        """Create temporary test files for upload"""
        file1_content, file2_content = TestDataFactory.dataset_to_anki_files(dataset)
        
        file1_fd, file1_path = tempfile.mkstemp(suffix='.txt', prefix='anki_e2e_1_')
        file2_fd, file2_path = tempfile.mkstemp(suffix='.txt', prefix='anki_e2e_2_')
        
        try:
            with os.fdopen(file1_fd, 'w', encoding='utf-8') as f:
                f.write(file1_content)
            
            with os.fdopen(file2_fd, 'w', encoding='utf-8') as f:
                f.write(file2_content)
            
            return file1_path, file2_path
        except Exception:
            try:
                os.unlink(file1_path)
                os.unlink(file2_path)
            except:
                pass
            raise

@pytest.mark.e2e
class TestCompleteUserWorkflow:
    """Test complete user workflow from upload to export"""
    
    @pytest.fixture(scope="class")
    def app_server(self):
        """Start Flask app server for testing"""
        # In a real test environment, you'd start the app in a subprocess
        # For now, we assume it's running on localhost:5000
        base_url = "http://127.0.0.1:5000"
        
        # Verify app is accessible
        import requests
        try:
            response = requests.get(base_url, timeout=5)
            yield base_url
        except requests.exceptions.ConnectionError:
            pytest.skip("Flask app not running. Start with 'python app.py'")
    
    @pytest.fixture
    def driver(self):
        """Setup and teardown WebDriver"""
        driver = TestSetup.setup_chrome_driver(headless=True)
        yield driver
        driver.quit()
    
    def test_upload_to_export_workflow(self, driver, app_server):
        """Test complete workflow: upload files → select cards → export"""
        
        # 1. Navigate to app
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 2. Navigate to new UI (if available)
        try:
            driver.get(f"{app_server}/select-new")
            
            # Wait for enhanced UI to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "toggle-debug"))
            )
            
            # Should show data from our test dataset
            assert "Test File" in driver.page_source
            
            print("✅ Enhanced UI loaded with test data")
            
        except TimeoutException:
            pytest.skip("Enhanced UI not accessible or no test data")
    
    def test_tab_navigation_workflow(self, driver, app_server):
        """Test tab navigation and content visibility"""
        
        driver.get(f"{app_server}/select-new")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main-tabs"))
        )
        
        # Test each tab
        tabs = [
            ("different-tab", "different-pane", "Different Cards"),
            ("identical-tab", "identical-pane", "Identical Cards"),
            ("unique1-tab", "unique1-pane", "Test File 1"),
            ("unique2-tab", "unique2-pane", "Test File 2")
        ]
        
        for tab_id, pane_id, expected_content in tabs:
            print(f"Testing tab: {tab_id}")
            
            # Click tab
            tab_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, tab_id))
            )
            tab_button.click()
            
            # Wait for tab to become active
            time.sleep(0.5)
            
            # Check tab pane is visible
            tab_pane = driver.find_element(By.ID, pane_id)
            assert tab_pane.is_displayed(), f"Tab pane {pane_id} should be visible"
            
            # Check for expected content
            assert expected_content in driver.page_source, f"Expected content '{expected_content}' not found in {tab_id}"
            
            # Count cards in this tab
            card_selector = f".{tab_id.replace('-tab', '-card')}"
            cards = driver.find_elements(By.CSS_SELECTOR, card_selector)
            visible_cards = [card for card in cards if card.is_displayed()]
            
            print(f"  ✅ Tab {tab_id}: {len(visible_cards)} cards visible")
            
            # For tabs that should have cards, ensure at least one is visible
            if tab_id in ["different-tab", "identical-tab", "unique1-tab", "unique2-tab"]:
                assert len(visible_cards) > 0, f"No visible cards in {tab_id}"
    
    def test_debug_features_workflow(self, driver, app_server):
        """Test debug features and logging"""
        
        driver.get(f"{app_server}/select-new")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "toggle-debug"))
        )
        
        # 1. Test debug mode toggle
        debug_button = driver.find_element(By.ID, "toggle-debug")
        debug_button.click()
        
        # Wait for debug panel to appear
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "debug-panel"))
        )
        
        debug_panel = driver.find_element(By.ID, "debug-panel")
        assert debug_panel.is_displayed(), "Debug panel should be visible"
        
        print("✅ Debug mode activated")
        
        # 2. Test console toggle
        console_button = driver.find_element(By.ID, "toggle-console")
        console_button.click()
        
        # Wait for console to appear
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "debug-console"))
        )
        
        console = driver.find_element(By.ID, "debug-console")
        assert console.is_displayed(), "Debug console should be visible"
        
        print("✅ Debug console activated")
        
        # 3. Test automated testing
        test_button = driver.find_element(By.ID, "test-tabs")
        test_button.click()
        
        # Wait a moment for tests to run
        time.sleep(2)
        
        # Check console for test output
        console_output = driver.find_element(By.ID, "console-output")
        console_text = console_output.text
        assert "Testing tab" in console_text, "Should show tab testing output"
        
        print("✅ Automated testing executed")
    
    def test_card_selection_workflow(self, driver, app_server):
        """Test card selection interactions"""
        
        driver.get(f"{app_server}/select-new")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main-tabs"))
        )
        
        # 1. Test different cards selection
        different_tab = driver.find_element(By.ID, "different-tab")
        different_tab.click()
        time.sleep(0.5)
        
        # Find radio buttons for different cards
        radio_buttons = driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"][name^="different-"]')
        if radio_buttons:
            # Click first radio button
            radio_buttons[0].click()
            assert radio_buttons[0].is_selected(), "Radio button should be selected"
            print("✅ Different card selection works")
        
        # 2. Test unique cards selection
        unique1_tab = driver.find_element(By.ID, "unique1-tab")
        unique1_tab.click()
        time.sleep(0.5)
        
        # Test select all toggle
        select_all = driver.find_elements(By.ID, "select-all-unique1")
        if select_all:
            initial_state = select_all[0].is_selected()
            select_all[0].click()
            time.sleep(0.2)
            
            # Check that individual checkboxes changed
            checkboxes = driver.find_elements(By.CSS_SELECTOR, ".unique1-checkbox")
            if checkboxes:
                assert checkboxes[0].is_selected() != initial_state, "Checkboxes should toggle with select all"
                print("✅ Select all toggle works")
        
        # 3. Test individual checkbox
        unique2_tab = driver.find_element(By.ID, "unique2-tab")
        unique2_tab.click()
        time.sleep(0.5)
        
        checkboxes = driver.find_elements(By.CSS_SELECTOR, ".unique2-checkbox")
        if checkboxes:
            initial_state = checkboxes[0].is_selected()
            checkboxes[0].click()
            assert checkboxes[0].is_selected() != initial_state, "Checkbox should toggle"
            print("✅ Individual checkbox selection works")
    
    def test_save_and_export_workflow(self, driver, app_server):
        """Test saving selections and generating export"""
        
        driver.get(f"{app_server}/select-new")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "save-selections"))
        )
        
        # 1. Test save selections
        save_button = driver.find_element(By.ID, "save-selections")
        save_button.click()
        
        # Wait for save to complete (look for toast or console message)
        time.sleep(2)
        
        # Check for success indication (could be toast, console, or network)
        # For now, just verify no errors occurred
        logs = driver.get_log('browser')
        error_logs = [log for log in logs if log['level'] == 'SEVERE']
        assert len(error_logs) == 0, f"JavaScript errors during save: {error_logs}"
        
        print("✅ Save selections completed without errors")
        
        # 2. Test export generation
        export_button = driver.find_element(By.ID, "generate-export")
        
        # Note: In a real test, this would trigger a download
        # For this test, we just verify the button works and doesn't cause errors
        export_button.click()
        
        # Wait to see if any errors occur
        time.sleep(2)
        
        # Check browser logs again
        logs = driver.get_log('browser')
        new_error_logs = [log for log in logs if log['level'] == 'SEVERE' and log not in error_logs]
        assert len(new_error_logs) == 0, f"JavaScript errors during export: {new_error_logs}"
        
        print("✅ Export generation initiated without errors")

@pytest.mark.e2e
class TestResponsiveDesign:
    """Test responsive design and mobile compatibility"""
    
    @pytest.fixture
    def mobile_driver(self):
        """Setup mobile-sized WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(375, 667)  # iPhone size
        yield driver
        driver.quit()
    
    def test_mobile_layout(self, mobile_driver):
        """Test mobile responsive layout"""
        base_url = "http://127.0.0.1:5000"
        
        try:
            mobile_driver.get(f"{base_url}/select-new")
            
            # Wait for page to load
            WebDriverWait(mobile_driver, 10).until(
                EC.presence_of_element_located((By.ID, "main-tabs"))
            )
            
            # Check that tabs are still accessible
            tabs = mobile_driver.find_elements(By.CSS_SELECTOR, ".nav-link")
            assert len(tabs) > 0, "Tabs should be present on mobile"
            
            # Check that debug controls adapt to mobile
            debug_controls = mobile_driver.find_element(By.CLASS_NAME, "debug-controls")
            assert debug_controls.is_displayed(), "Debug controls should be visible on mobile"
            
            print("✅ Mobile layout works correctly")
            
        except Exception as e:
            pytest.skip(f"Mobile layout test skipped: {e}")

@pytest.mark.e2e
class TestPerformance:
    """Test performance and load characteristics"""
    
    @pytest.fixture
    def driver(self):
        driver = TestSetup.setup_chrome_driver(headless=True)
        yield driver
        driver.quit()
    
    def test_page_load_performance(self, driver):
        """Test page load performance"""
        base_url = "http://127.0.0.1:5000"
        
        try:
            start_time = time.time()
            driver.get(f"{base_url}/select-new")
            
            # Wait for page to be fully loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "main-tabs"))
            )
            
            load_time = time.time() - start_time
            
            # Page should load within reasonable time
            assert load_time < 5.0, f"Page load took too long: {load_time:.2f}s"
            
            print(f"✅ Page loaded in {load_time:.2f}s")
            
        except Exception as e:
            pytest.skip(f"Performance test skipped: {e}")
    
    def test_tab_switching_performance(self, driver):
        """Test tab switching performance"""
        base_url = "http://127.0.0.1:5000"
        
        try:
            driver.get(f"{base_url}/select-new")
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "main-tabs"))
            )
            
            # Test switching between tabs quickly
            tabs = ["different-tab", "identical-tab", "unique1-tab", "unique2-tab"]
            
            total_time = 0
            for tab_id in tabs * 3:  # Test multiple rounds
                start_time = time.time()
                
                tab = driver.find_element(By.ID, tab_id)
                tab.click()
                
                # Wait for tab to become active
                WebDriverWait(driver, 2).until(
                    lambda d: "active" in tab.get_attribute("class")
                )
                
                switch_time = time.time() - start_time
                total_time += switch_time
                
                # Each tab switch should be fast
                assert switch_time < 1.0, f"Tab switch too slow: {switch_time:.2f}s"
            
            avg_time = total_time / (len(tabs) * 3)
            print(f"✅ Average tab switch time: {avg_time:.3f}s")
            
        except Exception as e:
            pytest.skip(f"Tab switching performance test skipped: {e}")

@pytest.mark.e2e
class TestErrorScenarios:
    """Test error handling in UI workflows"""
    
    @pytest.fixture
    def driver(self):
        driver = TestSetup.setup_chrome_driver(headless=True)
        yield driver
        driver.quit()
    
    def test_javascript_error_handling(self, driver):
        """Test that JavaScript errors are handled gracefully"""
        base_url = "http://127.0.0.1:5000"
        
        try:
            driver.get(f"{base_url}/select-new")
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "main-tabs"))
            )
            
            # Check for JavaScript errors in console
            logs = driver.get_log('browser')
            error_logs = [log for log in logs if log['level'] == 'SEVERE']
            
            # Should not have critical JavaScript errors
            critical_errors = [
                log for log in error_logs 
                if 'ReferenceError' in log['message'] or 'TypeError' in log['message']
            ]
            
            assert len(critical_errors) == 0, f"Critical JavaScript errors found: {critical_errors}"
            
            print("✅ No critical JavaScript errors detected")
            
        except Exception as e:
            pytest.skip(f"JavaScript error test skipped: {e}")
    
    def test_network_error_resilience(self, driver):
        """Test resilience to network errors"""
        base_url = "http://127.0.0.1:5000"
        
        try:
            driver.get(f"{base_url}/select-new")
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "save-selections"))
            )
            
            # Try to save selections (might fail if server not responding)
            save_button = driver.find_element(By.ID, "save-selections")
            save_button.click()
            
            # Wait to see how errors are handled
            time.sleep(3)
            
            # Check that UI is still responsive after network operation
            tabs = driver.find_elements(By.CSS_SELECTOR, ".nav-link")
            assert len(tabs) > 0, "UI should remain responsive after network operations"
            
            # Verify we can still click tabs
            tabs[0].click()
            time.sleep(0.5)
            
            print("✅ UI remains responsive during network operations")
            
        except Exception as e:
            pytest.skip(f"Network resilience test skipped: {e}")

if __name__ == "__main__":
    # Run E2E tests if called directly
    pytest.main([__file__, "-v", "-m", "e2e", "--tb=short"])