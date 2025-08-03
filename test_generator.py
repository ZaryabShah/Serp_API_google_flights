"""
Test suite for Google Flights URL generator.
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gfurl import build_gf_url, build_gf_url_from_serpapi, CABIN_CLASSES, STOPS_MAPPING
import urllib.parse

class TestGoogleFlightsURLGenerator(unittest.TestCase):
    """Test cases for the Google Flights URL generator."""
    
    def test_basic_oneway_flight(self):
        """Test basic one-way flight URL generation."""
        url = build_gf_url(
            legs=[{"from": "SYD", "to": "MEL", "date": "2025-08-15"}],
            pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0}
        )
        
        self.assertIn("google.com/travel/flights", url)
        self.assertIn("tfs=", url)
        self.assertIn("hl=en", url)
        self.assertIn("gl=US", url)
        self.assertIn("curr=USD", url)
        
        print(f"✅ One-way flight URL: {url}")
    
    def test_roundtrip_flight(self):
        """Test round-trip flight URL generation."""
        url = build_gf_url(
            legs=[
                {"from": "LAX", "to": "JFK", "date": "2025-08-15"},
                {"from": "JFK", "to": "LAX", "date": "2025-08-22"}
            ],
            pax={"adults": 2, "children": 1, "infants_in_seat": 0, "infants_on_lap": 0},
            cabin="BUSINESS",
            hl="en", gl="US", currency="USD"
        )
        
        self.assertIn("google.com/travel/flights", url)
        self.assertIn("tfs=", url)
        
        print(f"✅ Round-trip flight URL: {url}")
    
    def test_nonstop_filter(self):
        """Test nonstop filter."""
        url = build_gf_url(
            legs=[{"from": "SFO", "to": "ORD", "date": "2025-08-15"}],
            pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
            stops="NONSTOP"
        )
        
        self.assertIn("tfs=", url)
        print(f"✅ Nonstop flight URL: {url}")
    
    def test_airline_filter(self):
        """Test airline inclusion filter."""
        url = build_gf_url(
            legs=[{"from": "DFW", "to": "LAX", "date": "2025-08-15"}],
            pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
            include_airlines=["AA", "DL"]
        )
        
        self.assertIn("tfs=", url)
        print(f"✅ Airline filter URL: {url}")
    
    def test_time_window(self):
        """Test departure time window."""
        url = build_gf_url(
            legs=[{"from": "BOS", "to": "SEA", "date": "2025-08-15"}],
            pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
            dep_time_window=(6, 18)  # 6 AM to 6 PM
        )
        
        self.assertIn("tfs=", url)
        print(f"✅ Time window URL: {url}")
    
    def test_international_localization(self):
        """Test international localization settings."""
        url = build_gf_url(
            legs=[{"from": "SYD", "to": "MEL", "date": "2025-08-15"}],
            pax={"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
            hl="en", gl="AU", currency="AUD"
        )
        
        self.assertIn("hl=en", url)
        self.assertIn("gl=AU", url) 
        self.assertIn("curr=AUD", url)
        
        print(f"✅ Australian localization URL: {url}")
    
    def test_serpapi_compatibility(self):
        """Test SerpAPI parameter format compatibility."""
        serpapi_params = {
            "type": 2,  # Round-trip
            "departure_id": "LAX",
            "arrival_id": "JFK", 
            "outbound_date": "2025-08-15",
            "return_date": "2025-08-22",
            "adults": 1,
            "children": 0,
            "travel_class": 3,  # Business
            "max_stops": 0,  # Nonstop
            "hl": "en",
            "gl": "US",
            "currency": "USD"
        }
        
        url = build_gf_url_from_serpapi(serpapi_params)
        
        self.assertIn("google.com/travel/flights", url)
        self.assertIn("tfs=", url)
        
        print(f"✅ SerpAPI compatibility URL: {url}")
    
    def test_input_validation(self):
        """Test input validation."""
        
        # Test invalid airport code
        with self.assertRaises(ValueError):
            build_gf_url(
                legs=[{"from": "INVALID", "to": "MEL", "date": "2025-08-15"}]
            )
        
        # Test invalid date format
        with self.assertRaises(ValueError):
            build_gf_url(
                legs=[{"from": "SYD", "to": "MEL", "date": "2025/08/15"}]
            )
        
        # Test invalid cabin class
        with self.assertRaises(ValueError):
            build_gf_url(
                legs=[{"from": "SYD", "to": "MEL", "date": "2025-08-15"}],
                cabin="INVALID"
            )
        
        print("✅ Input validation tests passed")
    
    def test_complex_scenario(self):
        """Test complex flight scenario with multiple filters."""
        url = build_gf_url(
            legs=[
                {"from": "SFO", "to": "LHR", "date": "2025-09-01"},
                {"from": "LHR", "to": "SFO", "date": "2025-09-15"}
            ],
            pax={"adults": 2, "children": 1, "infants_in_seat": 0, "infants_on_lap": 1},
            cabin="PREMIUM_ECONOMY",
            stops="MAX_1", 
            include_airlines=["BA", "VS", "UA"],
            dep_time_window=(8, 20),
            arr_time_window=(6, 22),
            hl="en", gl="GB", currency="GBP"
        )
        
        self.assertIn("google.com/travel/flights", url)
        self.assertIn("tfs=", url)
        self.assertIn("hl=en", url)
        self.assertIn("gl=GB", url)
        self.assertIn("curr=GBP", url)
        
        print(f"✅ Complex scenario URL: {url}")
    
    def test_url_structure(self):
        """Test that generated URLs have proper structure."""
        url = build_gf_url(
            legs=[{"from": "DEN", "to": "MIA", "date": "2025-08-15"}]
        )
        
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)
        
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "www.google.com")
        self.assertEqual(parsed.path, "/travel/flights")
        self.assertIn("tfs", query_params)
        self.assertIn("hl", query_params)
        self.assertIn("gl", query_params)
        self.assertIn("curr", query_params)
        
        print("✅ URL structure validation passed")

def run_comprehensive_test():
    """Run a comprehensive test with various scenarios."""
    print("🚀 Running comprehensive Google Flights URL generator tests...\n")
    
    test_scenarios = [
        {
            "name": "Sydney to Melbourne (Economy, One-way)",
            "params": {
                "legs": [{"from": "SYD", "to": "MEL", "date": "2025-08-15"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "cabin": "ECONOMY",
                "hl": "en", "gl": "AU", "currency": "AUD"
            }
        },
        {
            "name": "Los Angeles to New York (Business, Round-trip, Nonstop)",
            "params": {
                "legs": [
                    {"from": "LAX", "to": "JFK", "date": "2025-08-15"},
                    {"from": "JFK", "to": "LAX", "date": "2025-08-22"}
                ],
                "pax": {"adults": 2, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "cabin": "BUSINESS",
                "stops": "NONSTOP",
                "hl": "en", "gl": "US", "currency": "USD"
            }
        },
        {
            "name": "London to Tokyo (First Class, with airline preference)",
            "params": {
                "legs": [{"from": "LHR", "to": "NRT", "date": "2025-09-01"}],
                "pax": {"adults": 1, "children": 0, "infants_in_seat": 0, "infants_on_lap": 0},
                "cabin": "FIRST",
                "include_airlines": ["BA", "JL"],
                "dep_time_window": (10, 16),
                "hl": "en", "gl": "GB", "currency": "GBP"
            }
        },
        {
            "name": "Family trip with children and infants",
            "params": {
                "legs": [
                    {"from": "SFO", "to": "CDG", "date": "2025-07-01"},
                    {"from": "CDG", "to": "SFO", "date": "2025-07-15"}
                ],
                "pax": {"adults": 2, "children": 2, "infants_in_seat": 1, "infants_on_lap": 0},
                "cabin": "PREMIUM_ECONOMY",
                "stops": "MAX_1",
                "hl": "en", "gl": "US", "currency": "USD"
            }
        }
    ]
    
    print("🧪 Test Scenarios:")
    print("=" * 80)
    
    for i, scenario in enumerate(test_scenarios, 1):
        try:
            print(f"\n{i}. {scenario['name']}")
            print("-" * 60)
            
            url = build_gf_url(**scenario['params'])
            
            print(f"🔗 URL: {url}")
            
            # Extract and display TFS payload for inspection
            parsed = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed.query)
            tfs_payload = query_params.get('tfs', [''])[0]
            
            print(f"📦 TFS Payload Length: {len(tfs_payload)} characters")
            print(f"🌍 Localization: hl={query_params.get('hl', [''])[0]}, gl={query_params.get('gl', [''])[0]}, curr={query_params.get('curr', [''])[0]}")
            print("✅ Generated successfully!")
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
    
    print(f"\n{'='*80}")
    print("🎉 Comprehensive test completed!")

if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "="*80)
    
    # Run comprehensive test
    run_comprehensive_test()
