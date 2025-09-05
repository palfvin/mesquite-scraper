#!/usr/bin/env python3
"""
Test runner for Mesquite Country Club scraper
Run this to test the scraper and catch issues like cookie banners
"""

import os
import sys
import subprocess

def run_tests():
    """Run the test suite"""
    print("🧪 Running Mesquite Country Club Scraper Tests")
    print("=" * 50)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = os.path.join(os.path.dirname(__file__), 'src')
    
    # Run specific tests that would catch the cookie banner issue
    critical_tests = [
        'test_scraper.TestMesquiteScraper.test_cookie_banner_detection',
        'test_scraper.TestMesquiteScraper.test_past_sales_link_clickability',
        'test_scraper.TestMesquiteScraper.test_full_click_sequence_with_cookie_handling'
    ]
    
    print("Running critical tests that would catch cookie banner issues:")
    for test in critical_tests:
        print(f"  • {test}")
    print()
    
    # Change to tests directory
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    try:
        # Run the tests
        result = subprocess.run([
            sys.executable, '-m', 'unittest', 
            'test_scraper.TestMesquiteScraper.test_cookie_banner_detection',
            'test_scraper.TestMesquiteScraper.test_past_sales_link_clickability',
            'test_scraper.TestMesquiteScraper.test_full_click_sequence_with_cookie_handling',
            '-v'
        ], cwd=test_dir, capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ All critical tests passed!")
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            print("This would have caught the cookie banner issue!")
            
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def run_all_tests():
    """Run all tests"""
    print("🧪 Running ALL Mesquite Country Club Scraper Tests")
    print("=" * 50)
    
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'unittest', 'discover', '-v'
        ], cwd=test_dir, capture_output=False)
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        exit_code = run_all_tests()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)