import os
import json
import tempfile
import uuid
import shutil
from typing import List, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from scraper import scrape_mesquite_properties
from utils import setup_logging
import config


def main():
    """
    Entry point for the Mesquite Country Club web scraping process.
    Scrapes property listings and extracts courtesy information.
    """
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Mesquite Country Club scraper")
    
    # Initialize Selenium WebDriver with Service
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    temp_dir = None  # No temp directory needed

    try:
        # Perform web scraping
        scraped_data = scrape_mesquite_properties(driver)

        # Validate and summarize the scraping results
        if scraped_data:
            print(f"Scraping complete. Retrieved data for {len(scraped_data)} properties.")
            for i, property_data in enumerate(scraped_data, 1):
                print(f"Property {i}: {property_data.get('address', 'Unknown address')} - "
                      f"Courtesy of: {property_data.get('courtesy_of', 'Not found')}")
        else:
            print("Scraping failed. No valid data retrieved.")

        # Write the data to a JSON file if available
        if scraped_data:
            # Find the directory at the same level as "src"
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_file_path = os.path.join(base_dir, "mesquite_properties.json")

            with open(output_file_path, "w", encoding="utf-8") as json_file:
                json.dump(scraped_data, json_file, indent=4, ensure_ascii=False)
            print(f"Data successfully written to {output_file_path}")
        else:
            print("No data available to write to file.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()
        # Clean up temporary directory
        if temp_dir:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


if __name__ == "__main__":
    main()