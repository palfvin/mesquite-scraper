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


def _dismiss_cookie_banner(driver: WebDriver):
    """Dismiss cookie consent banner if present."""
    try:
        # Look for common cookie banner dismiss buttons
        cookie_selectors = [
            "//div[contains(@class, 'cookie')]//button[contains(text(), 'Accept')]",
            "//div[contains(@class, 'cookie')]//button[contains(text(), 'OK')]",
            "//div[contains(@class, 'cookie')]//button[contains(text(), 'Close')]",
            "//div[contains(@class, 'cookie')]//button[@class='close']",
            "//div[contains(@class, 'cookie')]//a[contains(text(), 'Accept')]",
            "//div[contains(@class, 'cookie')]//span[contains(text(), '×')]",
            "//div[contains(@class, 'cookie-footer')]//button",
            "//div[contains(@class, 'cookie-footer')]//a",
            "//button[contains(@class, 'cookie')]",
            "//a[contains(@class, 'cookie')]"
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                cookie_button.click()
                print("Cookie banner dismissed")
                time.sleep(1)  # Wait for banner to disappear
                return True
            except TimeoutException:
                continue
                
        # If no clickable button found, try to hide the banner with JavaScript
        try:
            driver.execute_script("""
                var cookieElements = document.querySelectorAll('[class*="cookie"]');
                for (var i = 0; i < cookieElements.length; i++) {
                    cookieElements[i].style.display = 'none';
                }
            """)
            print("Cookie banner hidden with JavaScript")
            return True
        except:
            pass
            
        return False
        
    except Exception as e:
        print(f"Error handling cookie banner: {e}")
        return False


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
        
        # Dismiss cookie banner if present
        print("Checking for cookie banner...")
        _dismiss_cookie_banner(driver)
        
        # Click on "Past Sales" link (it's an anchor link to #properties-sold)
        print("Looking for 'Past Sales' link...")
        past_sales_link = WebDriverWait(driver, config.WEBDRIVER_TIMEOUT).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Past Sales"))
        )
        
        # Scroll to the element to ensure it's visible
        driver.execute_script("arguments[0].scrollIntoView(true);", past_sales_link)
        time.sleep(1)
        
        try:
            past_sales_link.click()
        except Exception as e:
            print(f"Regular click failed: {e}")
            print("Trying JavaScript click...")
            # Fallback to JavaScript click if regular click is intercepted
            driver.execute_script("arguments[0].click();", past_sales_link)
        
        _wait_for_page_load(driver)
        print("Successfully clicked on 'Past Sales'")
        
        # Add a pause to allow visual observation and for the page to scroll/load the section
        time.sleep(3)
        
        # Extract all property data from the listing table
        print("Extracting property data from listing table...")
        properties_data = _extract_all_listing_data(driver)
        
        print(f"Found {len(properties_data)} properties in the listing table")
        
        # Now visit each property page to get courtesy information
        for i, property_data in enumerate(properties_data, 1):
            property_url = property_data.get('url')
            if property_url:
                print(f"Getting courtesy info for property {i}/{len(properties_data)}: {property_data.get('address', 'Unknown')}")
                courtesy_info = _extract_courtesy_info(driver, property_url)
                property_data['courtesy_of'] = courtesy_info
                
                # Small delay to be respectful to the server and allow visual observation
                time.sleep(2)
            
    except TimeoutException:
        print("Error: Could not find 'Past Sales' link or page took too long to load")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return properties_data


def _extract_all_listing_data(driver: WebDriver) -> List[Dict[str, str]]:
    """
    Extract all property data from the listing table on the main page.
    
    Args:
        driver: The Selenium WebDriver instance.
        
    Returns:
        List of dictionaries containing property data from the table.
    """
    properties_data = []
    
    try:
        # Wait for the sold properties section to be visible
        time.sleep(3)
        
        # Get the page source and parse with BeautifulSoup for easier text processing
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the sold properties section by looking for the table headers
        # The headers are: Address List Date List Price List $ / Sq Ft Beds / Baths Sold Date Days on Market Sold Price Sold $ / Sq Ft
        
        # Find all property links first
        property_links = soup.find_all('a', href=lambda href: href and '/mesquite-country-club/' in href and not href.endswith('/mesquite-country-club/'))
        
        # Get the text content after the headers to parse the data
        page_text = soup.get_text()
        
        # Find the section with the table data (after "Address List Date List Price...")
        import re
        
        # Split the text to find property data rows
        # Look for the pattern that starts after the headers
        header_pattern = r'Address List Date List Price List \$ / Sq Ft Beds / Baths Sold Date Days on Market Sold Price Sold \$ / Sq Ft'
        
        if re.search(header_pattern, page_text):
            # Split by the header to get the data section
            parts = re.split(header_pattern, page_text)
            if len(parts) > 1:
                data_section = parts[1]
                
                # Process each property link and try to extract its data
                for link in property_links:
                    try:
                        property_data = {}
                        
                        # Get basic info from the link
                        property_data['url'] = link.get('href')
                        if not property_data['url'].startswith('http'):
                            property_data['url'] = 'https://www.pscondos.com' + property_data['url']
                        
                        address = link.get_text(strip=True)
                        property_data['address'] = address
                        
                        # Try to find this property's data in the data section
                        # Look for the address in the data section and extract the following data
                        address_pattern = re.escape(address)
                        
                        # Pattern to match the property data row
                        # Format: Address Date $Price $PricePerSqFt Beds/Baths Date Days $Price $PricePerSqFt
                        row_pattern = f'{address_pattern}\\s+(\\d{{4}}-\\d{{2}}-\\d{{2}})\\s+\\$(\\d{{1,3}}(?:,\\d{{3}})*)\\s+\\$(\\d+)\\s+(\\d+)\\s*/\\s*(\\d+\\.?\\d*)\\s+(\\d{{4}}-\\d{{2}}-\\d{{2}})\\s+(\\d+)\\s+\\$(\\d{{1,3}}(?:,\\d{{3}})*)\\s+\\$(\\d+)'
                        
                        match = re.search(row_pattern, data_section)
                        if match:
                            property_data['list_date'] = match.group(1)
                            property_data['list_price'] = f"${match.group(2)}"
                            property_data['list_price_per_sqft'] = f"${match.group(3)}"
                            property_data['beds'] = match.group(4)
                            property_data['baths'] = match.group(5)
                            property_data['sold_date'] = match.group(6)
                            property_data['days_on_market'] = match.group(7)
                            property_data['sold_price'] = f"${match.group(8)}"
                            property_data['sold_price_per_sqft'] = f"${match.group(9)}"
                        else:
                            # If exact pattern doesn't match, try to extract what we can
                            # Look for data near the address
                            address_index = data_section.find(address)
                            if address_index != -1:
                                # Get text around the address (next 200 characters)
                                surrounding_text = data_section[address_index:address_index + 200]
                                
                                # Extract dates
                                dates = re.findall(r'(\d{4}-\d{2}-\d{2})', surrounding_text)
                                if len(dates) >= 2:
                                    property_data['list_date'] = dates[0]
                                    property_data['sold_date'] = dates[1]
                                
                                # Extract prices
                                prices = re.findall(r'\$(\d{1,3}(?:,\d{3})*)', surrounding_text)
                                if len(prices) >= 2:
                                    property_data['list_price'] = f"${prices[0]}"
                                    property_data['sold_price'] = f"${prices[-1]}"
                                
                                # Extract beds/baths
                                beds_baths = re.search(r'(\d+)\s*/\s*(\d+\.?\d*)', surrounding_text)
                                if beds_baths:
                                    property_data['beds'] = beds_baths.group(1)
                                    property_data['baths'] = beds_baths.group(2)
                                
                                # Extract days on market (look for standalone number)
                                days_matches = re.findall(r'\b(\d{1,3})\b', surrounding_text)
                                for days in days_matches:
                                    if 1 <= int(days) <= 500:  # Reasonable range for days on market
                                        property_data['days_on_market'] = days
                                        break
                        
                        # Set defaults for missing fields
                        for field in ['list_date', 'list_price', 'list_price_per_sqft', 'beds', 'baths', 
                                     'sold_date', 'days_on_market', 'sold_price', 'sold_price_per_sqft']:
                            if field not in property_data:
                                property_data[field] = ''
                        
                        properties_data.append(property_data)
                        
                    except Exception as e:
                        print(f"Error extracting data for property {address}: {e}")
                        continue
        
        print(f"Extracted data for {len(properties_data)} properties from listing table")
        
    except Exception as e:
        print(f"Error extracting listing data: {e}")
    
    return properties_data


def _extract_courtesy_info(driver: WebDriver, property_url: str) -> str:
    """
    Extract courtesy information from an individual property page.
    
    Args:
        driver: The Selenium WebDriver instance.
        property_url: URL of the property page to scrape.
        
    Returns:
        Courtesy information string or "Not found" if extraction fails.
    """
    try:
        driver.get(property_url)
        _wait_for_page_load(driver)
        
        # Add a pause to allow visual observation of each property page
        time.sleep(2)
        
        # Extract courtesy information - based on actual HTML structure found
        try:
            # Look for the specific "Courtesy of:" text pattern found in the HTML
            courtesy_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Courtesy of:')]")
            courtesy_text = courtesy_element.text.strip()
            
            # Extract the actual agent/company name after "Courtesy of:"
            if "Courtesy of:" in courtesy_text:
                courtesy_of = courtesy_text.split("Courtesy of:")[-1].strip()
                return courtesy_of
            else:
                return courtesy_text
                
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
                        return courtesy_text
                except NoSuchElementException:
                    continue
        
        return "Not found"
        
    except Exception as e:
        print(f"Error extracting courtesy info for {property_url}: {e}")
        return "Not found"


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