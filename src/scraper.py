from typing import List, Dict, Optional
import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import config


def _wait_for_page_load(driver: WebDriver, timeout: int = config.WEBDRIVER_TIMEOUT):
    """Waits for the document.readyState to be 'complete'."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def scrape_mesquite_properties(driver: WebDriver) -> List[Dict[str, str]]:
    """
    Scrapes property listings from Mesquite Country Club Past Sales section.
    
    Args:
        driver: The Selenium WebDriver instance.
        
    Returns:
        A list of dictionaries containing property data with courtesy information.
    """
    properties_data = []
    
    try:
        # Navigate to the main page
        print(f"Navigating to {config.BASE_URL}")
        driver.get(config.BASE_URL)
        _wait_for_page_load(driver)
        
        # Click on "Past Sales" link (it's an anchor link to #properties-sold)
        print("Looking for 'Past Sales' link...")
        past_sales_link = WebDriverWait(driver, config.WEBDRIVER_TIMEOUT).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Past Sales"))
        )
        past_sales_link.click()
        _wait_for_page_load(driver)
        print("Successfully clicked on 'Past Sales'")
        
        # Add a pause to allow visual observation and for the page to scroll/load the section
        time.sleep(3)
        
        # Find all property links in the Past Sales section
        print("Finding property listings...")
        # Look for links that contain the mesquite-country-club path (more specific)
        property_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/mesquite-country-club/']")
        property_urls = []
        
        for link in property_links:
            href = link.get_attribute("href")
            if href and "/mesquite-country-club/" in href and href not in property_urls:
                # Filter out the main community page link
                if not href.endswith("/mesquite-country-club/"):
                    property_urls.append(href)
        
        print(f"Found {len(property_urls)} property listings")
        
        # Visit each property page to extract courtesy information
        for i, property_url in enumerate(property_urls, 1):
            print(f"Processing property {i}/{len(property_urls)}: {property_url}")
            property_data = _extract_property_data(driver, property_url)
            if property_data:
                properties_data.append(property_data)
            
            # Small delay to be respectful to the server and allow visual observation
            time.sleep(2)
            
    except TimeoutException:
        print("Error: Could not find 'Past Sales' link or page took too long to load")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return properties_data


def _extract_property_data(driver: WebDriver, property_url: str) -> Optional[Dict[str, str]]:
    """
    Extracts property data including courtesy information from a property page.
    
    Args:
        driver: The Selenium WebDriver instance.
        property_url: URL of the property page to scrape.
        
    Returns:
        Dictionary containing property data or None if extraction fails.
    """
    try:
        driver.get(property_url)
        _wait_for_page_load(driver)
        
        # Add a pause to allow visual observation of each property page
        time.sleep(2)
        
        property_data = {
            "url": property_url,
            "address": "Not found",
            "courtesy_of": "Not found"
        }
        
        # Extract property address - based on actual HTML structure
        try:
            # The address is in an h1 tag based on the HTML structure we found
            address_element = driver.find_element(By.TAG_NAME, "h1")
            property_data["address"] = address_element.text.strip()
        except NoSuchElementException:
            # Fallback selectors
            try:
                address_element = driver.find_element(By.XPATH, "//h1 | //*[contains(@class, 'address')] | //*[contains(text(), 'Mesquite')]")
                property_data["address"] = address_element.text.strip()
            except NoSuchElementException:
                print(f"Could not find address for property: {property_url}")
        
        # Extract courtesy information - based on actual HTML structure found
        try:
            # Look for the specific "Courtesy of:" text pattern found in the HTML
            courtesy_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Courtesy of:')]")
            courtesy_text = courtesy_element.text.strip()
            
            # Extract the actual agent/company name after "Courtesy of:"
            if "Courtesy of:" in courtesy_text:
                courtesy_of = courtesy_text.split("Courtesy of:")[-1].strip()
                property_data["courtesy_of"] = courtesy_of
            else:
                property_data["courtesy_of"] = courtesy_text
                
        except NoSuchElementException:
            # Fallback to other possible selectors
            fallback_selectors = [
                "//*[contains(text(), 'courtesy of')]",
                "//*[contains(text(), 'Listing courtesy of')]",
                "//span[contains(@class, 'courtesy')]",
                "//div[contains(@class, 'courtesy')]"
            ]
            
            for selector in fallback_selectors:
                try:
                    courtesy_element = driver.find_element(By.XPATH, selector)
                    courtesy_text = courtesy_element.text.strip()
                    if courtesy_text:
                        property_data["courtesy_of"] = courtesy_text
                        break
                except NoSuchElementException:
                    continue
            
            if property_data["courtesy_of"] == "Not found":
                print(f"Could not find courtesy information for property: {property_url}")
            else:
                print(f"Found courtesy info: {property_data['courtesy_of']}")
                
        except Exception as e:
            print(f"Error extracting courtesy info for {property_url}: {e}")
        
        return property_data
        
    except Exception as e:
        print(f"Error processing property {property_url}: {e}")
        return None