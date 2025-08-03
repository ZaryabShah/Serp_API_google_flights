"""
Command-line interface for Google Flights URL generator.
"""

import click
import json
from datetime import datetime
from gfurl import build_gf_url, CABIN_CLASSES, STOPS_MAPPING

@click.command()
@click.option('--from', 'origin', required=True, help='Origin airport code (e.g., SYD)')
@click.option('--to', 'destination', required=True, help='Destination airport code (e.g., MEL)')
@click.option('--depart', required=True, help='Departure date (YYYY-MM-DD)')
@click.option('--return', 'return_date', help='Return date for round-trip (YYYY-MM-DD)')
@click.option('--adults', default=1, help='Number of adults (default: 1)')
@click.option('--children', default=0, help='Number of children (default: 0)')
@click.option('--infants-seat', default=0, help='Number of infants in seat (default: 0)')
@click.option('--infants-lap', default=0, help='Number of infants on lap (default: 0)')
@click.option('--cabin', default='ECONOMY', 
              type=click.Choice(['ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST']),
              help='Cabin class (default: ECONOMY)')
@click.option('--stops', default='ANY',
              type=click.Choice(['ANY', 'NONSTOP', 'MAX_1', 'MAX_2']),
              help='Stop preference (default: ANY)')
@click.option('--include-airlines', help='Comma-separated airline codes to include (e.g., QF,BA)')
@click.option('--exclude-airlines', help='Comma-separated airline codes to exclude')
@click.option('--dep-time', help='Departure time window as "HH:MM-HH:MM" (e.g., "06:00-18:00")')
@click.option('--arr-time', help='Arrival time window as "HH:MM-HH:MM"')
@click.option('--hl', default='en', help='Language code (default: en)')
@click.option('--gl', default='US', help='Country code (default: US)')
@click.option('--currency', default='USD', help='Currency code (default: USD)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
def main(origin, destination, depart, return_date, adults, children, infants_seat, infants_lap,
         cabin, stops, include_airlines, exclude_airlines, dep_time, arr_time, 
         hl, gl, currency, json_output):
    """
    Generate Google Flights URLs from command line inputs.
    
    Examples:
    
    One-way flight:
    python -m cli --from SYD --to MEL --depart 2025-08-15 --adults 1
    
    Round-trip flight:
    python -m cli --from SYD --to MEL --depart 2025-08-15 --return 2025-08-20 --adults 2 --cabin BUSINESS
    
    With filters:
    python -m cli --from LAX --to JFK --depart 2025-08-15 --stops NONSTOP --include-airlines AA,DL
    """
    
    try:
        # Build legs list
        legs = [{"from": origin.upper(), "to": destination.upper(), "date": depart}]
        
        if return_date:
            legs.append({"from": destination.upper(), "to": origin.upper(), "date": return_date})
        
        # Build passenger dictionary
        pax = {
            "adults": adults,
            "children": children, 
            "infants_in_seat": infants_seat,
            "infants_on_lap": infants_lap
        }
        
        # Parse airline lists
        include_list = include_airlines.split(',') if include_airlines else None
        exclude_list = exclude_airlines.split(',') if exclude_airlines else None
        
        # Parse time windows
        dep_time_window = None
        if dep_time:
            start_time, end_time = dep_time.split('-')
            start_hour = int(start_time.split(':')[0])
            end_hour = int(end_time.split(':')[0])
            dep_time_window = (start_hour, end_hour)
            
        arr_time_window = None
        if arr_time:
            start_time, end_time = arr_time.split('-')
            start_hour = int(start_time.split(':')[0])
            end_hour = int(end_time.split(':')[0])
            arr_time_window = (start_hour, end_hour)
        
        # Generate URL
        url = build_gf_url(
            legs=legs,
            pax=pax,
            cabin=cabin,
            stops=stops,
            include_airlines=include_list,
            exclude_airlines=exclude_list,
            dep_time_window=dep_time_window,
            arr_time_window=arr_time_window,
            hl=hl,
            gl=gl,
            currency=currency
        )
        
        if json_output:
            result = {
                "url": url,
                "parameters": {
                    "legs": legs,
                    "passengers": pax,
                    "cabin": cabin,
                    "stops": stops,
                    "include_airlines": include_list,
                    "exclude_airlines": exclude_list,
                    "localization": {"hl": hl, "gl": gl, "currency": currency}
                }
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"\n✅ Generated Google Flights URL:")
            click.echo(f"🔗 {url}")
            click.echo(f"\n📋 Flight Details:")
            click.echo(f"   • Route: {origin.upper()} → {destination.upper()}")
            click.echo(f"   • Departure: {depart}")
            if return_date:
                click.echo(f"   • Return: {return_date}")
            click.echo(f"   • Passengers: {adults} adults, {children} children, {infants_seat} infants (seat), {infants_lap} infants (lap)")
            click.echo(f"   • Cabin: {cabin}")
            click.echo(f"   • Stops: {stops}")
            if include_list:
                click.echo(f"   • Include Airlines: {', '.join(include_list)}")
            if exclude_list:
                click.echo(f"   • Exclude Airlines: {', '.join(exclude_list)}")
            click.echo(f"   • Locale: {hl}-{gl}, Currency: {currency}")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        exit(1)

if __name__ == '__main__':
    main()
