import base64
import json
from urllib.parse import urlencode

def build_gf_url(
    origin: str = None,
    destination: str = None,
    depart_date: str = None,
    return_date: str = None,
    legs: list = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "ECONOMY",
    nonstop: bool = False,
    currency: str = "USD",
    locale: str = "en",
    country: str = "US"
) -> str:
    """
    Generate Google Flights URL with encoded tfs parameter
    
    :param origin: Departure airport IATA code (for simple trips)
    :param destination: Arrival airport IATA code (for simple trips)
    :param depart_date: Outbound date in YYYY-MM-DD format
    :param return_date: Return date in YYYY-MM-DD format (for round trips)
    :param legs: List of flight legs for complex itineraries
        [{"origin": "SYD", "destination": "MEL", "date": "2025-08-15"}, ...]
    :param adults: Number of adult passengers
    :param children: Number of child passengers
    :param infants: Number of infant passengers
    :param cabin: Cabin class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
    :param nonstop: Nonstop flights only
    :param currency: Currency code (e.g. USD, EUR, AUD)
    :param locale: Language code (e.g. en, fr, de)
    :param country: Country code (e.g. US, AU, GB)
    
    :return: Google Flights URL with encoded parameters
    """
    # Validate inputs
    if not legs:
        if not origin or not destination or not depart_date:
            raise ValueError("Missing required parameters for simple trip")
        legs = [{"origin": origin, "destination": destination, "date": depart_date}]
        if return_date:
            legs.append({"origin": destination, "destination": origin, "date": return_date})
    
    # Build TFS structure
    tfs_list = []
    for idx, leg in enumerate(legs):
        flight_set = {
            "leg": [{
                "origin": leg["origin"].upper(),
                "destination": leg["destination"].upper(),
                "date": leg["date"]
            }]
        }
        
        # Add parameters only to the first flight segment
        if idx == 0:
            flight_set.update({
                "passengers": {
                    "adultCount": adults,
                    "childCount": children,
                    "infantInLapCount": infants
                },
                "cabin": cabin
            })
        
        if nonstop:
            flight_set["nonstop"] = True
        
        tfs_list.append(flight_set)
    
    # Convert to JSON and encode
    tfs_json = json.dumps(tfs_list, separators=(",", ":"))
    tfs_b64 = base64.urlsafe_b64encode(tfs_json.encode()).decode()
    tfs_b64 = tfs_b64.replace("=", "")  # Remove padding
    
    # Build URL parameters
    params = {
        "tfs": tfs_b64,
        "hl": locale,
        "gl": country,
        "curr": currency
    }
    
    return f"https://www.google.com/travel/flights?{urlencode(params)}"

# Example usage
if __name__ == "__main__":
    # Round trip example
    url = build_gf_url(
        origin="SYD",
        destination="MEL",
        depart_date="2025-08-15",
        return_date="2025-08-20",
        adults=1,
        cabin="ECONOMY",
        currency="AUD",
        locale="en",
        country="AU"
    )
    print("Round trip URL:")
    print(url)
    
    # Multi-city example
    url = build_gf_url(
        legs=[
            {"origin": "JFK", "destination": "LHR", "date": "2025-09-10"},
            {"origin": "LHR", "destination": "CDG", "date": "2025-09-15"},
            {"origin": "CDG", "destination": "JFK", "date": "2025-09-20"}
        ],
        adults=2,
        children=1,
        cabin="BUSINESS",
        nonstop=True,
        currency="USD"
    )
    print("\nMulti-city URL:")
    print(url)