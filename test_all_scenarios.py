"""
Comprehensive test of gpt3.py - Generate URLs for all SerpAPI scenarios
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SerpAPI import build_gf_urls, build_serpapi_params

def test_scenario(name, **kwargs):
    """Test a scenario and print the results"""
    print(f"\n{'='*60}")
    print(f"🧪 {name}")
    print('='*60)
    
    try:
        result = build_gf_urls(**kwargs)
        
        print(f"📊 Generated {len(result['links'])} URL(s)")
        
        for i, link in enumerate(result['links'], 1):
            print(f"\n🔗 URL {i}:")
            print(link['url'])
            
            coverage = link['coverage']
            if coverage['encoded']:
                print(f"✅ Encoded: {', '.join(coverage['encoded'])}")
            if coverage['approximated']:
                print(f"⚠️  Approximated: {', '.join(coverage['approximated'])}")
            if coverage['unmatched']:
                print(f"❌ Unmatched: {', '.join(coverage['unmatched'])}")
        
        if result['unmatched_global']:
            print(f"\n🌐 Global unmatched: {', '.join(result['unmatched_global'])}")
            
        # Show SerpAPI fallback params
        serpapi_params = result['serpapi_fallback'] 
        print(f"\n📋 SerpAPI fallback params: {len(serpapi_params)} parameters")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 COMPREHENSIVE GOOGLE FLIGHTS URL GENERATOR TEST")
    print("Testing all SerpAPI scenarios with gpt3.py implementation")
    
    # 1. Basic one-way flight
    test_scenario(
        "Basic One-Way Flight",
        departure_id="LAX",
        arrival_id="JFK", 
        outbound_date="2025-08-15",
        type="2",  # One-way
        adults=1
    )
    
    # 2. Round-trip with filters
    test_scenario(
        "Round-Trip with Business Class and Nonstop",
        departure_id="SYD",
        arrival_id="MEL",
        outbound_date="2025-08-15", 
        return_date="2025-08-20",
        type="1",  # Round-trip
        travel_class="3",  # Business
        stops="1",  # Nonstop
        adults=2,
        children=1,
        hl="en",
        gl="AU", 
        currency="AUD"
    )
    
    # 3. Family trip with time windows
    test_scenario(
        "Family Trip with Time Windows",
        departure_id="DFW",
        arrival_id="LAX",
        outbound_date="2025-09-01",
        return_date="2025-09-08", 
        type="1",
        adults=2,
        children=2,
        infants_in_seat=1,
        travel_class="2",  # Premium Economy
        outbound_times="8,18",  # 8AM-6PM departure
        return_times="10,20,12,22",  # 10AM-8PM dep, 12PM-10PM arr
        stops="2"  # Max 1 stop
    )
    
    # 4. Multi-airport search
    test_scenario(
        "Multi-Airport Search (Paris airports to London airports)",
        departure_id="CDG,ORY",
        arrival_id="LHR,LGW,STN",
        outbound_date="2025-08-15",
        return_date="2025-08-22",
        type="1",
        adults=1,
        travel_class="4",  # First class
        include_airlines="BA,AF,KL",
        hl="en",
        gl="GB",
        currency="GBP"
    )
    
    # 5. Airline filtering
    test_scenario(
        "Airline Include/Exclude Filtering",
        departure_id="SFO",
        arrival_id="NRT",
        outbound_date="2025-10-01",
        adults=1,
        type="2",  # One-way
        include_airlines="UA,NH,JL",  # United, ANA, JAL
        stops="1",  # Nonstop
        outbound_times="12,18"  # Afternoon departure
    )
    
    # 6. Multi-city journey
    test_scenario(
        "Multi-City Journey",
        type="3",
        multi_city_json='[{"departure_id":"NYC","arrival_id":"LON","date":"2025-08-15"},{"departure_id":"LON","arrival_id":"PAR","date":"2025-08-20"},{"departure_id":"PAR","arrival_id":"NYC","date":"2025-08-25"}]',
        adults=1,
        travel_class="3",  # Business
        hl="en",
        gl="US",
        currency="USD"
    )
    
    # 7. Advanced filters (these will be unmatched but tracked)
    test_scenario(
        "Advanced Filters (SerpAPI-only features)",
        departure_id="BOS",
        arrival_id="MIA",
        outbound_date="2025-08-15",
        return_date="2025-08-20",
        type="1",
        adults=1,
        travel_class="1",  # Economy
        stops="2",  # Max 1 stop
        bags=2,  # 2 carry-on bags
        max_price=500,  # Max $500
        sort_by="2",  # Sort by price
        emissions="1",  # Less emissions only
        layover_duration="90,300",  # 1.5h - 5h layovers
        exclude_conns="DFW,ORD",  # Exclude Dallas and Chicago connections
        max_duration=480,  # Max 8 hours
        deep_search=True,
        show_hidden=True
    )
    
    # 8. International with alliances
    test_scenario(
        "International with Star Alliance",
        departure_id="/m/0d5_c",  # Wikidata ID for Frankfurt
        arrival_id="SIN",
        outbound_date="2025-11-01",
        return_date="2025-11-15",
        type="1",
        adults=2,
        travel_class="3",  # Business
        include_airlines="STAR_ALLIANCE",
        outbound_times="20,6",  # Evening/night departure
        return_times="14,20",  # Afternoon departure
        hl="de",
        gl="DE",
        currency="EUR"
    )
    
    # 9. Budget domestic with max stops
    test_scenario(
        "Budget Domestic with Multiple Stops",
        departure_id="SEA",
        arrival_id="MIA", 
        outbound_date="2025-08-15",
        type="2",  # One-way
        adults=1,
        travel_class="1",  # Economy
        stops="3",  # Max 2 stops (cheapest option)
        exclude_airlines="DL,AA",  # Exclude major carriers
        outbound_times="5,10,18,23"  # Early morning or late evening
    )
    
    # 10. Luxury long-haul
    test_scenario(
        "Luxury Long-Haul with Premium Preferences",
        departure_id="JFK",
        arrival_id="DXB",
        outbound_date="2025-12-20",
        return_date="2026-01-05",
        type="1",
        adults=2,
        travel_class="4",  # First class
        stops="1",  # Nonstop preferred
        include_airlines="EK,QR,LH",  # Emirates, Qatar, Lufthansa
        outbound_times="18,23",  # Evening departure
        return_times="8,14",  # Morning/afternoon return
        hl="en",
        gl="AE",
        currency="AED"
    )
    
    # 11. Complex family trip
    test_scenario(
        "Complex Family Trip with Mixed Ages",
        departure_id="ORD",
        arrival_id="FCO",
        outbound_date="2025-07-01",
        return_date="2025-07-14", 
        type="1",
        adults=2,
        children=3,
        infants_in_seat=1,
        infants_on_lap=1,
        travel_class="2",  # Premium Economy
        stops="2",  # Max 1 stop
        outbound_times="10,16",  # Mid-day departure
        hl="it",
        gl="IT",
        currency="EUR"
    )
    
    # 12. Business traveler same-day return
    test_scenario(
        "Same-Day Business Return",
        departure_id="BOS",
        arrival_id="DCA",
        outbound_date="2025-08-15",
        return_date="2025-08-15",  # Same day
        type="1",
        adults=1,
        travel_class="3",  # Business
        stops="1",  # Nonstop
        outbound_times="6,9",  # Early morning
        return_times="18,21",  # Evening return
        include_airlines="DL,AA,UA"  # Major carriers
    )
    
    print(f"\n{'='*60}")
    print("🎉 ALL TESTS COMPLETED!")
    print("📋 Copy the URLs above and test them in your browser")
    print("✅ Each URL should open Google Flights with the correct search parameters")
    print('='*60)

if __name__ == "__main__":
    main()
