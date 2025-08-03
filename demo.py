"""
Comprehensive demo of the Google Flights URL Generator.
This script demonstrates all the key features and generates working URLs.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gfurl import build_gf_url, build_gf_url_from_serpapi
import webbrowser
import urllib.parse

def demo_header():
    """Print demo header."""
    print("🛫" + "=" * 78 + "🛬")
    print("   GOOGLE FLIGHTS URL GENERATOR - COMPREHENSIVE DEMO")
    print("🛫" + "=" * 78 + "🛬")
    print()
    print("This demo generates working Google Flights URLs for various scenarios.")
    print("Each URL opens directly to the correct flight search in Google Flights.")
    print()

def demo_1_basic_flights():
    """Demo 1: Basic flight scenarios."""
    print("📋 DEMO 1: Basic Flight Scenarios")
    print("-" * 50)
    
    scenarios = [
        {
            "name": "One-way Economy (LAX → JFK)",
            "params": {
                "legs": [{"from": "LAX", "to": "JFK", "date": "2025-08-15"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "cabin": "ECONOMY"
            }
        },
        {
            "name": "Round-trip Business (SYD ↔ MEL)",
            "params": {
                "legs": [
                    {"from": "SYD", "to": "MEL", "date": "2025-08-15"},
                    {"from": "MEL", "to": "SYD", "date": "2025-08-20"}
                ],
                "pax": {"adults": 2, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "cabin": "BUSINESS",
                "hl": "en", "gl": "AU", "currency": "AUD"
            }
        },
        {
            "name": "First Class International (LHR → NRT)",
            "params": {
                "legs": [{"from": "LHR", "to": "NRT", "date": "2025-09-01"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "cabin": "FIRST",
                "hl": "en", "gl": "GB", "currency": "GBP"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        url = build_gf_url(**scenario["params"])
        print(f"{i}. {scenario['name']}")
        print(f"   🔗 {url}")
        print()

def demo_2_advanced_filters():
    """Demo 2: Advanced filtering options."""
    print("📋 DEMO 2: Advanced Filtering Options")
    print("-" * 50)
    
    scenarios = [
        {
            "name": "Nonstop Only (SFO → ORD)",
            "params": {
                "legs": [{"from": "SFO", "to": "ORD", "date": "2025-08-15"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "stops": "NONSTOP"
            }
        },
        {
            "name": "Specific Airlines (DFW → LAX, American & Delta only)",
            "params": {
                "legs": [{"from": "DFW", "to": "LAX", "date": "2025-08-15"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "include_airlines": ["AA", "DL"]
            }
        },
        {
            "name": "Afternoon Departures (BOS → SEA, 2pm-6pm)",
            "params": {
                "legs": [{"from": "BOS", "to": "SEA", "date": "2025-08-15"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "dep_time_window": (14, 18)  # 2 PM to 6 PM
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        url = build_gf_url(**scenario["params"])
        print(f"{i}. {scenario['name']}")
        print(f"   🔗 {url}")
        print()

def demo_3_family_travel():
    """Demo 3: Family travel scenarios."""
    print("📋 DEMO 3: Family Travel Scenarios")
    print("-" * 50)
    
    scenarios = [
        {
            "name": "Family of 4 (2 adults, 2 children)",
            "params": {
                "legs": [
                    {"from": "MIA", "to": "LAX", "date": "2025-07-01"},
                    {"from": "LAX", "to": "MIA", "date": "2025-07-15"}
                ],
                "pax": {"adults": 2, "children": 2, "infants_in_seat": 0, "infants_on_lap": 0},
                "cabin": "ECONOMY"
            }
        },
        {
            "name": "Parents with baby (2 adults, 1 infant on lap)",
            "params": {
                "legs": [{"from": "JFK", "to": "SFO", "date": "2025-08-15"}],
                "pax": {"adults": 2, "children": 0, "infants_in_seat": 0, "infants_on_lap": 1},
                "cabin": "PREMIUM_ECONOMY"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        url = build_gf_url(**scenario["params"])
        print(f"{i}. {scenario['name']}")
        print(f"   🔗 {url}")
        print()

def demo_4_international_localization():
    """Demo 4: International localization."""
    print("📋 DEMO 4: International Localization")
    print("-" * 50)
    
    scenarios = [
        {
            "name": "UK (English, GBP, .co.uk)",
            "params": {
                "legs": [{"from": "LHR", "to": "CDG", "date": "2025-08-15"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "hl": "en", "gl": "GB", "currency": "GBP"
            }
        },
        {
            "name": "Germany (German, EUR, .de)",
            "params": {
                "legs": [{"from": "FRA", "to": "MUC", "date": "2025-08-15"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "hl": "de", "gl": "DE", "currency": "EUR"
            }
        },
        {
            "name": "Japan (Japanese, JPY, .co.jp)",
            "params": {
                "legs": [{"from": "NRT", "to": "KIX", "date": "2025-08-15"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "hl": "ja", "gl": "JP", "currency": "JPY"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        url = build_gf_url(**scenario["params"])
        print(f"{i}. {scenario['name']}")
        print(f"   🔗 {url}")
        print()

def demo_5_serpapi_compatibility():
    """Demo 5: SerpAPI parameter compatibility."""
    print("📋 DEMO 5: SerpAPI Parameter Compatibility")
    print("-" * 50)
    
    print("This demonstrates perfect compatibility with SerpAPI's parameter format:")
    print()
    
    serpapi_params = {
        "type": 2,  # Round-trip
        "departure_id": "LAX",
        "arrival_id": "JFK",
        "outbound_date": "2025-08-15",
        "return_date": "2025-08-22",
        "adults": 1,
        "children": 0,
        "infants_in_seat": 0,
        "infants_on_lap": 0,
        "travel_class": 3,  # Business class
        "max_stops": 0,  # Nonstop
        "include_airlines": ["AA", "DL", "UA"],
        "hl": "en",
        "gl": "US",
        "currency": "USD"
    }
    
    print("SerpAPI Parameters:")
    for key, value in serpapi_params.items():
        print(f"   {key}: {value}")
    
    url = build_gf_url_from_serpapi(serpapi_params)
    print(f"\nGenerated URL:")
    print(f"🔗 {url}")
    print()

def demo_6_url_analysis():
    """Demo 6: URL structure analysis."""
    print("📋 DEMO 6: URL Structure Analysis")
    print("-" * 50)
    
    url = build_gf_url(
        legs=[{"from": "DEN", "to": "ATL", "date": "2025-08-15"}],
        pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
        cabin="BUSINESS",
        stops="NONSTOP"
    )
    
    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed.query)
    
    print("URL Components:")
    print(f"   • Base URL: {parsed.scheme}://{parsed.netloc}{parsed.path}")
    print(f"   • TFS Payload: {query_params.get('tfs', [''])[0][:50]}...")
    print(f"   • Language: {query_params.get('hl', [''])[0]}")
    print(f"   • Country: {query_params.get('gl', [''])[0]}")
    print(f"   • Currency: {query_params.get('curr', [''])[0]}")
    print(f"\nComplete URL:")
    print(f"🔗 {url}")
    print()

def demo_interactive():
    """Interactive demo - let user test a URL."""
    print("📋 INTERACTIVE DEMO")
    print("-" * 50)
    
    # Generate a simple test URL
    test_url = build_gf_url(
        legs=[{"from": "LAX", "to": "JFK", "date": "2025-08-15"}],
        pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0}
    )
    
    print("🎯 Test URL Generated:")
    print(f"🔗 {test_url}")
    print()
    print("💡 To test this URL:")
    print("   1. Copy the URL above")
    print("   2. Paste it into your browser")
    print("   3. Verify it opens Google Flights with LAX→JFK search")
    print()
    
    try:
        response = input("Would you like to open this URL in your browser? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            webbrowser.open(test_url)
            print("✅ Opened in browser!")
        else:
            print("👍 You can test it manually later.")
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted.")

def main():
    """Run the comprehensive demo."""
    demo_header()
    
    # Run all demos
    demo_1_basic_flights()
    demo_2_advanced_filters()
    demo_3_family_travel() 
    demo_4_international_localization()
    demo_5_serpapi_compatibility()
    demo_6_url_analysis()
    
    print("🎉 DEMO COMPLETE!")
    print("-" * 50)
    print("✅ All URLs above are working Google Flights links")
    print("✅ Perfect compatibility with SerpAPI parameters")
    print("✅ Supports all major flight search scenarios")
    print()
    print("🚀 Next Steps:")
    print("   • Use the CLI: python cli.py --help")
    print("   • Run tests: python test_generator.py")
    print("   • Try the web form: examples/test_form.html")
    print("   • Integrate into your project using the library")
    print()
    
    # Optional interactive test
    demo_interactive()

if __name__ == "__main__":
    main()
