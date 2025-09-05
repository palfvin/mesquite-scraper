# Mesquite Country Club Property Scraper

A web scraper built in the style of amherst-office-scraper that extracts property listing courtesy information from the Mesquite Country Club properties on pscondos.com.

## Features

- Navigates to the Mesquite Country Club page
- Clicks on "Past Sales" section (anchor link to #properties-sold)
- Extracts property listings from the sold properties section
- Visits each individual property page to extract "Courtesy of:" information
- Saves results to JSON file with address, URL, and courtesy details
- Comprehensive error handling and logging
- Visible browser mode for watching the scraper work

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Chrome/Chromium is installed on your system

## Usage

Run the scraper:
```bash
cd src
python main.py
```

The scraper will:
1. Navigate to https://www.pscondos.com/palm-springs/mesquite-country-club/
2. Click on the "Past Sales" link
3. Find all property listings
4. Visit each property page to extract courtesy information
5. Save results to `mesquite_properties.json`

## Data Analysis

After scraping, analyze the realtor and company data:

```bash
python analyze_data.py
```

This will generate:
- **Console summary** with top realtors and companies by property count
- **Market share analysis** showing percentage breakdowns
- **Detailed report** saved to `property_analysis_report.txt`

See [ANALYSIS.md](ANALYSIS.md) for detailed documentation.

## Output

The scraper generates a JSON file with the following structure:
```json
[
  {
    "url": "https://www.pscondos.com/property/...",
    "address": "Property address",
    "courtesy_of": "Agent/Company name"
  }
]
```

## Configuration

Edit `src/config.py` to modify:
- `BASE_URL` - Target website URL
- `WEBDRIVER_TIMEOUT` - Page load timeout in seconds
- `HEADLESS_MODE` - Set to `False` to show browser window, `True` to run hidden
- `WINDOW_WIDTH` / `WINDOW_HEIGHT` - Browser window dimensions

### Visible Browser Mode
By default, the scraper runs with a visible Chrome browser window so you can watch it work:
- Set `HEADLESS_MODE = False` in `config.py` to see the browser
- Set `HEADLESS_MODE = True` to run in background mode
- Window size and position are configurable

## Architecture

The project follows the same structure as amherst-office-scraper:

- `src/main.py` - Entry point and orchestration
- `src/scraper.py` - Core scraping logic
- `src/config.py` - Configuration settings
- `src/utils.py` - Utility functions and logging

## Testing

The project includes comprehensive tests that catch real-world issues like cookie banners:

### Run Critical Tests (Recommended)
```bash
python run_tests.py
```
This runs the key tests that would catch blocking issues:
- Cookie banner detection
- Past Sales link clickability 
- Full click sequence with cookie handling

### Run All Tests
```bash
python run_tests.py --all
```

### Test Coverage
- ✅ Page loading and basic functionality
- ✅ Cookie banner detection and dismissal
- ✅ Element clickability (catches intercepted clicks)
- ✅ Property link detection after navigation
- ✅ Full scraping workflow validation

**Note**: The `test_past_sales_link_clickability` test would have caught the original cookie banner issue by detecting the `ElementClickInterceptedException`.

## Error Handling

The scraper includes comprehensive error handling for:
- Network timeouts
- Missing elements
- Page load failures
- Chrome driver issues
- Cookie banner interference

## Notes

- The scraper runs with a visible browser window by default (configurable)
- Includes respectful delays between requests for observation and server courtesy
- Handles dynamic content loading
- No authentication required (unlike amherst-office-scraper)
- Visual feedback and slower execution when running in visible mode