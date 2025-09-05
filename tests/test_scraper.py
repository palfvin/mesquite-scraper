import unittest
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import config
from scraper import _dismiss_cookie_banner


class TestMesquiteScraper(unittest.TestCase):
    """Test suite for Mesquite Country Club scraper"""
    
    @classmethod
    def setUpClass(cls):
        """Set up Chrome driver for all tests"""
        options = webdriver.ChromeOptions()
        # Run in visible mode for testing to see what's happening
        if os.getenv('HEADLESS_TEST', 'false').lower() == 'true':
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1200,800")
        
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up driver after all tests"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
    
    def setUp(self):
        """Navigate to the main page before each test"""
        print(f"\nNavigating to {config.BASE_URL}")
        self.driver.get(config.BASE_URL)
        time.sleep(2)  # Allow page to load
    
    def test_page_loads_successfully(self):
        """Test that the main page loads without errors"""
        self.assertIn("Mesquite Country Club", self.driver.title)
        self.assertIn("Palm Springs", self.driver.page_source)
    
    def test_cookie_banner_detection(self):
        """Test that detects if cookie banners are present and blocking"""
        print("Checking for cookie banners...")
        
        # Look for cookie-related elements
        cookie_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'cookie')]")
        
        if cookie_elements:
            print(f"Found {len(cookie_elements)} cookie-related elements")
            for i, element in enumerate(cookie_elements[:3]):  # Check first 3
                try:
                    if element.is_displayed():
                        print(f"Cookie element {i+1}: {element.tag_name} - class: {element.get_attribute('class')}")
                        print(f"  Text: {element.text[:100]}...")
                        print(f"  Size: {element.size}")
                        print(f"  Location: {element.location}")
                except:
                    pass
        else:
            print("No cookie elements found")
    
    def test_past_sales_link_exists(self):
        """Test that the Past Sales link exists and is findable"""
        print("Looking for Past Sales link...")
        
        try:
            past_sales_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Past Sales"))
            )
            self.assertTrue(past_sales_link.is_displayed(), "Past Sales link should be visible")
            print(f"Past Sales link found: {past_sales_link.text}")
            print(f"Link location: {past_sales_link.location}")
            print(f"Link size: {past_sales_link.size}")
            
        except TimeoutException:
            self.fail("Past Sales link not found within timeout period")
    
    def test_past_sales_link_clickability(self):
        """Test that the Past Sales link is actually clickable (this would have caught the cookie issue)"""
        print("Testing Past Sales link clickability...")
        
        try:
            past_sales_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Past Sales"))
            )
            
            # Try to click and catch the specific error we encountered
            try:
                past_sales_link.click()
                print("✅ Past Sales link clicked successfully")
                
            except ElementClickInterceptedException as e:
                print(f"❌ COOKIE BANNER ISSUE DETECTED: {e}")
                print("This is the exact error that would occur!")
                
                # Show what element is blocking
                if "Other element would receive the click" in str(e):
                    print("Another element is blocking the click - likely a cookie banner")
                
                # This test would FAIL and expose the issue
                self.fail(f"Past Sales link is blocked by another element: {e}")
                
        except TimeoutException:
            self.fail("Past Sales link not clickable within timeout period")
    
    def test_cookie_banner_dismissal(self):
        """Test that cookie banner can be dismissed"""
        print("Testing cookie banner dismissal...")
        
        # Check if cookie banner is present before dismissal
        cookie_elements_before = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'cookie')]")
        visible_before = [elem for elem in cookie_elements_before if elem.is_displayed()]
        
        if visible_before:
            print(f"Found {len(visible_before)} visible cookie elements before dismissal")
            
            # Try to dismiss cookie banner
            success = _dismiss_cookie_banner(self.driver)
            time.sleep(2)  # Wait for dismissal to take effect
            
            # Check if cookie banner is gone after dismissal
            cookie_elements_after = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'cookie')]")
            visible_after = [elem for elem in cookie_elements_after if elem.is_displayed()]
            
            print(f"Found {len(visible_after)} visible cookie elements after dismissal")
            
            if success:
                self.assertLess(len(visible_after), len(visible_before), 
                               "Cookie banner should be dismissed or hidden")
            else:
                print("Cookie banner dismissal reported as unsuccessful")
        else:
            print("No visible cookie banners found to dismiss")
    
    def test_full_click_sequence_with_cookie_handling(self):
        """Test the complete sequence: dismiss cookies, then click Past Sales"""
        print("Testing full click sequence with cookie handling...")
        
        # Step 1: Dismiss cookie banner
        print("Step 1: Dismissing cookie banner...")
        _dismiss_cookie_banner(self.driver)
        time.sleep(2)
        
        # Step 2: Try to click Past Sales
        print("Step 2: Clicking Past Sales link...")
        try:
            past_sales_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Past Sales"))
            )
            
            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", past_sales_link)
            time.sleep(1)
            
            # Try click
            past_sales_link.click()
            print("✅ Full sequence completed successfully")
            
            # Verify we're in the right section
            time.sleep(3)
            self.assertIn("properties-sold", self.driver.current_url or self.driver.page_source)
            
        except ElementClickInterceptedException as e:
            self.fail(f"Click still intercepted after cookie handling: {e}")
    
    def test_property_links_detection(self):
        """Test that property links can be found after clicking Past Sales"""
        print("Testing property links detection...")
        
        # First dismiss cookies and click Past Sales
        _dismiss_cookie_banner(self.driver)
        time.sleep(1)
        
        try:
            past_sales_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Past Sales"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", past_sales_link)
            time.sleep(1)
            past_sales_link.click()
            time.sleep(3)
            
            # Look for property links
            property_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/mesquite-country-club/']")
            property_urls = []
            
            for link in property_links:
                href = link.get_attribute("href")
                if href and "/mesquite-country-club/" in href and not href.endswith("/mesquite-country-club/"):
                    property_urls.append(href)
            
            print(f"Found {len(property_urls)} property links")
            self.assertGreater(len(property_urls), 0, "Should find at least one property link")
            
            # Print first few for verification
            for i, url in enumerate(property_urls[:3]):
                print(f"Property {i+1}: {url}")
                
        except Exception as e:
            self.fail(f"Failed to detect property links: {e}")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)