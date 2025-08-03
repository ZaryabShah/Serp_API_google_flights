"""
URL validator for Google Flights URLs using Playwright.
"""

import asyncio
import sys
from playwright.async_api import async_playwright
import urllib.parse
import json

async def validate_google_flights_url(url: str, headless: bool = True) -> dict:
    """
    Validate a Google Flights URL by opening it in a browser and checking the results.
    
    Args:
        url: The Google Flights URL to validate
        headless: Whether to run browser in headless mode
        
    Returns:
        Dictionary with validation results
    """
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print(f"🌐 Opening URL: {url}")
            
            # Navigate to the URL
            await page.goto(url, wait_until="networkidle")
            
            # Wait for the page to load
            await page.wait_for_timeout(3000)
            
            # Check if we're on the correct page
            title = await page.title()
            print(f"📄 Page title: {title}")
            
            validation_results = {
                "url": url,
                "status": "success",
                "page_title": title,
                "errors": [],
                "warnings": [],
                "extracted_data": {}
            }
            
            # Check if we landed on Google Flights
            if "google.com/travel/flights" in page.url:
                validation_results["extracted_data"]["correct_domain"] = True
                print("✅ Successfully reached Google Flights")
                
                # Try to extract flight search parameters from the page
                try:
                    # Wait for search form to load
                    await page.wait_for_selector('[data-value]', timeout=5000)
                    
                    # Extract origin and destination if visible
                    origin_elements = await page.query_selector_all('[data-value][aria-label*="rom"]')
                    dest_elements = await page.query_selector_all('[data-value][aria-label*="o"]')
                    
                    if origin_elements:
                        origin = await origin_elements[0].get_attribute('data-value')
                        validation_results["extracted_data"]["origin"] = origin
                        print(f"🛫 Origin detected: {origin}")
                    
                    if dest_elements:
                        dest = await dest_elements[0].get_attribute('data-value') 
                        validation_results["extracted_data"]["destination"] = dest
                        print(f"🛬 Destination detected: {dest}")
                        
                    # Check for passenger count
                    passenger_elements = await page.query_selector_all('[data-value*="adult"]')
                    if passenger_elements:
                        passenger_text = await passenger_elements[0].inner_text()
                        validation_results["extracted_data"]["passengers"] = passenger_text
                        print(f"👥 Passengers: {passenger_text}")
                        
                except Exception as e:
                    validation_results["warnings"].append(f"Could not extract all search parameters: {str(e)}")
                    print(f"⚠️  Warning: Could not extract search parameters: {str(e)}")
                
            else:
                validation_results["status"] = "warning"
                validation_results["warnings"].append(f"Redirected to: {page.url}")
                print(f"⚠️  Warning: Redirected to {page.url}")
            
            # Check for any error messages on the page
            error_selectors = [
                '[role="alert"]',
                '.error-message',
                '[class*="error"]',
                '[data-testid*="error"]'
            ]
            
            for selector in error_selectors:
                error_elements = await page.query_selector_all(selector)
                for element in error_elements:
                    error_text = await element.inner_text()
                    if error_text.strip():
                        validation_results["errors"].append(error_text.strip())
                        print(f"❌ Error found: {error_text.strip()}")
            
            # Take a screenshot for debugging
            screenshot_path = "validation_screenshot.png"
            await page.screenshot(path=screenshot_path)
            validation_results["screenshot"] = screenshot_path
            print(f"📸 Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            validation_results = {
                "url": url,
                "status": "error", 
                "errors": [str(e)],
                "warnings": [],
                "extracted_data": {}
            }
            print(f"❌ Error during validation: {str(e)}")
            
        finally:
            await browser.close()
            
        return validation_results

async def main():
    """Main function for CLI usage."""
    if len(sys.argv) != 2:
        print("Usage: python validate_url.py <google_flights_url>")
        print("\nExample:")
        print("python validate_url.py 'https://www.google.com/travel/flights?tfs=...'")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print("🚀 Starting Google Flights URL validation...")
    print("=" * 60)
    
    results = await validate_google_flights_url(url, headless=True)
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)
    
    print(f"Status: {results['status'].upper()}")
    
    if results['errors']:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"   • {error}")
    
    if results['warnings']:
        print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
        for warning in results['warnings']:
            print(f"   • {warning}")
    
    if results['extracted_data']:
        print(f"\n📋 Extracted Data:")
        for key, value in results['extracted_data'].items():
            print(f"   • {key}: {value}")
    
    # Save full results to JSON
    with open('validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Full results saved to: validation_results.json")
    
    if results['status'] == 'success':
        print(f"\n✅ URL validation completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ URL validation completed with issues.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
