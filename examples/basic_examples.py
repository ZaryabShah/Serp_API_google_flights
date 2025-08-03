"""
Basic examples of using the Google Flights URL generator.
"""

import sys
import os

# Add the parent directory to the path to import gfurl
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gfurl import build_gf_url, build_gf_url_from_serpapi

def example_1_simple_oneway():
    """Example 1: Simple one-way flight"""
    print("Example 1: Simple one-way flight (Sydney to Melbourne)")
    print("-" * 60)
    
    url = build_gf_url(
        legs=[{"from": "SYD", "to": "MEL", "date": "2025-08-15"}],
        pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
        hl="en", gl="AU", currency="AUD"
    )
    
    print(f"🔗 URL: {url}")
    print("✅ Use this URL to search for one-way flights from Sydney to Melbourne\n")

def example_2_roundtrip_business():
    """Example 2: Round-trip business class flight"""
    print("Example 2: Round-trip business class flight (LAX to JFK)")
    print("-" * 60)
    
    url = build_gf_url(
        legs=[
            {"from": "LAX", "to": "JFK", "date": "2025-08-15"},
            {"from": "JFK", "to": "LAX", "date": "2025-08-22"}
        ],
        pax={"adults": 2, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
        cabin="BUSINESS",
        stops="NONSTOP",
        hl="en", gl="US", currency="USD"
    )
    
    print(f"🔗 URL: {url}")
    print("✅ Use this URL to search for nonstop business class round-trip flights\n")

def example_3_family_with_filters():
    """Example 3: Family trip with filters"""
    print("Example 3: Family trip with airline and time preferences")
    print("-" * 60)
    
    url = build_gf_url(
        legs=[
            {"from": "SFO", "to": "LHR", "date": "2025-07-01"},
            {"from": "LHR", "to": "SFO", "date": "2025-07-15"}
        ],
        pax={"adults": 2, "children": 2, "infants_in_seat": 0, "infants_on_lap": 1},
        cabin="PREMIUM_ECONOMY",
        stops="MAX_1",
        include_airlines=["BA", "VS", "UA"],
        dep_time_window=(8, 20),  # Depart between 8 AM and 8 PM
        hl="en", gl="US", currency="USD"
    )
    
    print(f"🔗 URL: {url}")
    print("✅ Family-friendly flight search with preferred airlines and times\n")

def example_4_serpapi_format():
    """Example 4: Using SerpAPI parameter format"""
    print("Example 4: Using SerpAPI parameter format")
    print("-" * 60)
    
    serpapi_params = {
        "type": 2,  # Round-trip
        "departure_id": "DEN",
        "arrival_id": "MIA",
        "outbound_date": "2025-09-01",
        "return_date": "2025-09-08",
        "adults": 1,
        "children": 0,
        "infants_in_seat": 0,
        "infants_on_lap": 0,
        "travel_class": 3,  # Business class
        "max_stops": 0,  # Nonstop
        "include_airlines": ["AA", "DL"],
        "hl": "en",
        "gl": "US",
        "currency": "USD"
    }
    
    url = build_gf_url_from_serpapi(serpapi_params)
    
    print(f"🔗 URL: {url}")
    print("✅ Generated from SerpAPI-style parameters\n")

def example_5_international_localization():
    """Example 5: International flights with local settings"""
    print("Example 5: International flights with local settings")
    print("-" * 60)
    
    # Flight from Tokyo to Sydney, using Japanese locale and Japanese Yen
    url = build_gf_url(
        legs=[{"from": "NRT", "to": "SYD", "date": "2025-10-15"}],
        pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
        cabin="ECONOMY",
        hl="ja", gl="JP", currency="JPY"
    )
    
    print(f"🔗 URL: {url}")
    print("✅ Japanese localization for Tokyo to Sydney flight\n")

def example_6_multi_stop_preferences():
    """Example 6: Different stop preferences"""
    print("Example 6: Comparing different stop preferences")
    print("-" * 60)
    
    base_params = {
        "legs": [{"from": "SEA", "to": "MIA", "date": "2025-08-20"}],
        "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
        "hl": "en", "gl": "US", "currency": "USD"
    }
    
    stop_options = ["NONSTOP", "MAX_1", "MAX_2", "ANY"]
    
    for stops in stop_options:
        url = build_gf_url(stops=stops, **base_params)
        print(f"🔗 {stops}: {url}")
    
    print("✅ Compare URLs for different stop preferences\n")

def example_7_cabin_class_comparison():
    """Example 7: Different cabin classes"""
    print("Example 7: Comparing different cabin classes")
    print("-" * 60)
    
    base_params = {
        "legs": [{"from": "ORD", "to": "LAX", "date": "2025-08-25"}],
        "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
        "hl": "en", "gl": "US", "currency": "USD"
    }
    
    cabins = ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]
    
    for cabin in cabins:
        url = build_gf_url(cabin=cabin, **base_params)
        print(f"🔗 {cabin}: {url}")
    
    print("✅ Compare URLs for different cabin classes\n")

def main():
    """Run all examples"""
    print("🚀 Google Flights URL Generator - Examples")
    print("=" * 80)
    print()
    
    examples = [
        example_1_simple_oneway,
        example_2_roundtrip_business,
        example_3_family_with_filters,
        example_4_serpapi_format,
        example_5_international_localization,
        example_6_multi_stop_preferences,
        example_7_cabin_class_comparison
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ Error in {example.__name__}: {str(e)}\n")
    
    print("=" * 80)
    print("🎉 All examples completed!")
    print("\n💡 Tips:")
    print("   • Copy any URL and paste it into your browser to test")
    print("   • Modify the parameters to suit your needs")
    print("   • Use the CLI tool for quick URL generation")
    print("   • Run the validator to confirm URLs work correctly")

if __name__ == "__main__":
    main()
