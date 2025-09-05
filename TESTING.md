# Testing Guide

## Why These Tests Would Have Caught the Cookie Banner Issue

The original error you encountered was:
```
ElementClickInterceptedException: Element <a class="nav-item nav-link" data-toggle="pill" href="#properties-sold">...</a> is not clickable at point (877, 567). Other element would receive the click: <div class="cookie-footer display">...</div>
```

## Tests That Expose This Issue

### 1. `test_past_sales_link_clickability`
This test specifically tries to click the Past Sales link and catches `ElementClickInterceptedException`:

```python
def test_past_sales_link_clickability(self):
    try:
        past_sales_link.click()
        print("✅ Past Sales link clicked successfully")
    except ElementClickInterceptedException as e:
        print(f"❌ COOKIE BANNER ISSUE DETECTED: {e}")
        self.fail(f"Past Sales link is blocked by another element: {e}")
```

**This test would have FAILED** and shown exactly the error you encountered.

### 2. `test_cookie_banner_detection`
This test looks for cookie-related elements and reports their visibility:

```python
def test_cookie_banner_detection(self):
    cookie_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'cookie')]")
    if cookie_elements:
        print(f"Found {len(cookie_elements)} cookie-related elements")
        # Reports size, location, visibility of cookie banners
```

### 3. `test_full_click_sequence_with_cookie_handling`
This test verifies the complete fix works:

```python
def test_full_click_sequence_with_cookie_handling(self):
    # Step 1: Dismiss cookie banner
    _dismiss_cookie_banner(self.driver)
    # Step 2: Try to click Past Sales
    past_sales_link.click()  # Should work now
```

## Running the Tests

### Quick Test (Catches Cookie Issues)
```bash
python run_tests.py
```

### All Tests
```bash
python run_tests.py --all
```

### Individual Test
```bash
cd tests
python -m unittest test_scraper.TestMesquiteScraper.test_past_sales_link_clickability -v
```

## What the Tests Show

**Before Fix** (would have failed):
```
❌ COOKIE BANNER ISSUE DETECTED: element click intercepted
FAIL: test_past_sales_link_clickability
```

**After Fix** (should pass):
```
✅ Past Sales link clicked successfully
OK: test_past_sales_link_clickability
```

## Test Environment

- Tests run with visible browser by default (set `HEADLESS_TEST=true` to run headless)
- Tests use the same Chrome options as the main scraper
- Each test navigates to the page fresh to simulate real conditions

## Why Static Analysis Missed This

The `web_read()` function I used only gets the initial HTML, not:
- JavaScript-rendered content
- Dynamic elements like cookie banners
- Interactive behaviors
- Geographic/session-specific content

**Real browser testing** is essential for catching these issues!