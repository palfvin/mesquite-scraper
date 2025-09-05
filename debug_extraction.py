#!/usr/bin/env python3
"""
Debug script to test the data extraction without running the full scraper
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import config
from scraper import _dismiss_cookie_banner, _extract_all_listing_data

def debug_extraction():
    """Debug the data extraction process"""
    print("🔍 Debug: Testing data extraction...")
    
    # Initialize Chrome driver
    options = webdriver.ChromeOptions()
    if config.HEADLESS_MODE:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to the page
        print(f"Navigating to {config.BASE_URL}")
        driver.get(config.BASE_URL)
        time.sleep(3)
        
        # Dismiss cookie banner
        print("Dismissing cookie banner...")
        _dismiss_cookie_banner(driver)
        
        # Click Past Sales
        print("Clicking Past Sales...")
        past_sales_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Past Sales"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", past_sales_link)
        time.sleep(1)
        
        try:
            past_sales_link.click()
        except:
            driver.execute_script("arguments[0].click();", past_sales_link)
        
        time.sleep(5)  # Wait for content to load
        
        # Debug: Check what's on the page
        print("Checking page content...")
        page_text = driver.page_source
        
        # Look for key indicators
        if "Address List Date" in page_text:
            print("✅ Found table headers in page")
        else:
            print("❌ Table headers not found")
        
        # Count property links
        property_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/mesquite-country-club/']")
        filtered_links = [link for link in property_links if not link.get_attribute("href").endswith("/mesquite-country-club/")]
        print(f"Found {len(filtered_links)} property links")
        
        # Show first few links
        for i, link in enumerate(filtered_links[:3]):
            print(f"  {i+1}. {link.text} -> {link.get_attribute('href')}")
        
        # Try extraction
        print("\nTesting extraction...")
        properties_data = _extract_all_listing_data(driver)
        
        print(f"\n📊 EXTRACTION RESULTS:")
        print(f"Total properties extracted: {len(properties_data)}")
        
        # Show first few properties
        for i, prop in enumerate(properties_data[:3]):
            print(f"\nProperty {i+1}:")
            for key, value in prop.items():
                print(f"  {key}: {value}")
        
        return len(properties_data) > 0
        
    except Exception as e:
        print(f"Error during debug: {e}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = debug_extraction()
    if success:
        print("\n✅ Debug completed successfully")
    else:
        print("\n❌ Debug found issues")