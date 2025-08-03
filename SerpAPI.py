"""
gf_url_builder.py
─────────────────
Build Google Flights URLs (canonical ?tfs= form) from SerpApi-like inputs.

Goals:
- Encode everything Google supports in the tfs payload.
- Accept SerpApi parameters one-to-one where possible.
- For features not representable in a URL, report them and provide a SerpApi payload.

Installation:
    pip install fast-flights==2.*

Usage:
    from gf_url_builder import build_gf_urls, build_serpapi_params

    urls = build_gf_urls(
        departure_id="SYD",
        arrival_id="MEL",
        outbound_date="2025-08-15",
        return_date="2025-08-20",
        travel_class="1",          # 1=Economy, 2=Premium, 3=Business, 4=First
        stops="1",                 # 0=Any, 1=Nonstop, 2=1 stop or fewer, 3=2 stops or fewer
        include_airlines="QF",
        outbound_times="6,18",
        hl="en", gl="AU", currency="AUD",
        adults=1
    )
    for u in urls["links"]:
        print("🔗", u["url"], "coverage:", u["coverage"])

    serp = build_serpapi_params(...same kwargs...)
"""

from __future__ import annotations
import itertools
import json
import re
import urllib.parse as _u
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Iterable, List, Optional, Tuple

# fast-flights (protobuf encoder)
from fast_flights.filter import TFSData
from fast_flights.flights_impl import FlightData, Passengers

# ─────────────────────────────────────────────────────────────────────────────
# Helpers & validation
# ─────────────────────────────────────────────────────────────────────────────

_IATA_RE = re.compile(r"^[A-Z0-9]{3}$")
_KGMID_RE = re.compile(r"^/m/[A-Za-z0-9_]+$")

def _is_airport_or_place(s: str) -> bool:
    return bool(_IATA_RE.match(s) or _KGMID_RE.match(s))

def _validate_airport_or_place(code: str) -> None:
    if not _is_airport_or_place(code):
        raise ValueError(f"Invalid code '{code}'. Expect IATA (e.g., SYD) or kgmid (e.g., /m/0vzm).")

def _validate_iso_date(iso: str) -> None:
    try:
        date.fromisoformat(iso)
    except Exception as e:
        raise ValueError(f"Invalid date '{iso}': {e}")

def _csv_to_list(s: Optional[str]) -> List[str]:
    if not s:
        return []
    return [p.strip() for p in s.split(",") if p.strip()]

def _q(v: str) -> str:
    return _u.quote_plus(v, safe="")

# Parse SerpApi time windows like "4,18" or "4,18,3,19"
def _parse_time_window(win: Optional[str]) -> Tuple[Optional[Tuple[int,int]], Optional[Tuple[int,int]]]:
    if not win:
        return None, None
    parts = [p.strip() for p in win.split(",")]
    try:
        ints = list(map(int, parts))
    except ValueError:
        return None, None
    if len(ints) == 2:
        return (ints[0], ints[1]), None
    if len(ints) == 4:
        return (ints[0], ints[1]), (ints[2], ints[3])
    return None, None

# SerpApi enumerations → local
_TRAVEL_CLASS = {"1": "economy", "2": "premium-economy", "3": "business", "4": "first"}
_STOPS_MAP = {  # SerpApi: 0=Any, 1=Nonstop, 2=1 stop or fewer, 3=2 stops or fewer
    "0": None,
    "1": 0,
    "2": 1,
    "3": 2,
}

@dataclass
class Coverage:
    encoded: List[str] = field(default_factory=list)    # params fully encoded into tfs or query
    approximated: List[str] = field(default_factory=list) # partially mapped
    unmatched: List[str] = field(default_factory=list)  # not representable in URL

@dataclass
class LinkOut:
    url: str
    coverage: Coverage

# ─────────────────────────────────────────────────────────────────────────────
# Core: Build one Google Flights URL from one pair of (from, to)
# ─────────────────────────────────────────────────────────────────────────────

def _build_single_url(
    *,
    dep: str,
    arr: str,
    outbound_date: str,
    return_date: Optional[str],
    type: Optional[str],
    travel_class: Optional[str],
    adults: int,
    children: int,
    infants_in_seat: int,
    infants_on_lap: int,
    stops: Optional[str],
    include_airlines: List[str],
    exclude_airlines: List[str],
    outbound_times: Optional[str],
    return_times: Optional[str],
    hl: str,
    gl: str,
    currency: str,
) -> LinkOut:
    # Validation
    _validate_airport_or_place(dep)
    _validate_airport_or_place(arr)
    _validate_iso_date(outbound_date)
    if return_date:
        _validate_iso_date(return_date)

    legs: List[FlightData] = [FlightData(date=outbound_date, from_airport=dep, to_airport=arr)]
    round_trip = False

    # Trip type
    declared_type = type  # SerpApi: 1=Round, 2=One-way, 3=Multi
    if declared_type == "2":       # one-way
        pass
    elif declared_type == "1" or (return_date is not None and declared_type is None):
        # Round trip if return_date provided or type=1
        round_trip = True
        # For round trip, Google expects the exact inverse leg
        legs.append(FlightData(date=return_date, from_airport=arr, to_airport=dep))
    elif declared_type in (None, "3"):
        # We'll treat this specific builder as two-leg max;
        # Multi-city is handled by build_gf_urls when multiple dates/legs are passed via multi_city_json.
        # Here, if return_date is None and type is None, it's one-way. If type=3, unmatched handled upstream.
        pass

    # Passengers
    pax = Passengers(
        adults=max(0, adults),
        children=max(0, children),
        infants_in_seat=max(0, infants_in_seat),
        infants_on_lap=max(0, infants_on_lap),
    )

    cov = Coverage()

    # Seat / Cabin
    seat = None
    if travel_class and travel_class in _TRAVEL_CLASS:
        seat = _TRAVEL_CLASS[travel_class]
        cov.encoded.append("travel_class")
    elif travel_class:
        cov.unmatched.append(f"travel_class ({travel_class})")

    # Stops
    max_stops = None
    if stops is not None:
        if stops in _STOPS_MAP:
            max_stops = _STOPS_MAP[stops]
            cov.encoded.append("stops")
        else:
            cov.unmatched.append(f"stops ({stops})")

    # Time windows
    # SerpApi provides outbound_times and return_times separately.
    # We map dep/arr windows for leg 0 and leg 1 respectively when present.
    dep0, arr0 = _parse_time_window(outbound_times)
    dep1, arr1 = _parse_time_window(return_times) if round_trip else (None, None)

    # Compose TFS
    # Prefer passing only fields that the installed fast-flights supports.
    # Minimal required fields:
    tfs_kwargs: Dict = dict(
        flight_data=legs,
        trip="round-trip" if round_trip else "one-way",
        passengers=pax,
    )
    if seat:
        tfs_kwargs["seat"] = seat
    if max_stops is not None:
        tfs_kwargs["max_stops"] = max_stops

    # Attempt to pass include/exclude airlines & per-leg time windows if your fast-flights supports them.
    # We detect feature support by looking at TFSData.from_interface signature through trial.
    def _try_kw(key: str, value):
        try:
            TFSData.from_interface(**{**tfs_kwargs, key: value})
            tfs_kwargs[key] = value
            cov.encoded.append(key)
            return True
        except TypeError:
            cov.unmatched.append(f"{key} (not supported by installed fast-flights)")
            return False

    if include_airlines:
        _try_kw("include_airlines", include_airlines)
    if exclude_airlines:
        _try_kw("exclude_airlines", exclude_airlines)

    # Windows: fast-flights (>=2.x) commonly exposes dep/arr hour windows per leg.
    # We pass tuples for leg 0 and leg 1 if available.
    if dep0:
        _try_kw("dep_time_window", dep0)  # global dep window or leg0 depending on fast-flights
    if arr0:
        _try_kw("arr_time_window", arr0)
    # For return leg:
    if round_trip and (dep1 or arr1):
        # Some builds support per-leg arrays: dep_time_windows=[(d0,d1),(d2,d3)]
        # Try multi-leg first; fallback to unmatched if not accepted.
        added = False
        if dep1 or arr1:
            try:
                probe = dict(tfs_kwargs)
                probe["dep_time_windows"] = [dep0, dep1]
                probe["arr_time_windows"] = [arr0, arr1]
                TFSData.from_interface(**probe)
                tfs_kwargs["dep_time_windows"] = [dep0, dep1]
                tfs_kwargs["arr_time_windows"] = [arr0, arr1]
                cov.encoded.append("dep_time_windows/arr_time_windows")
                added = True
            except TypeError:
                pass
        if not added and (dep1 or arr1):
            cov.approximated.append("return_times (per-leg windows unsupported; only outbound applied)")

    # Build tfs payload
    tfs = TFSData.from_interface(**tfs_kwargs).as_b64().decode()
    cov.encoded.extend(["tfs", "hl", "gl", "currency"])

    url = (
        "https://www.google.com/travel/flights?"
        f"tfs={_q(tfs)}&hl={_q(hl)}&gl={_q(gl)}&curr={_q(currency)}"
    )

    # Things that do not map to URL at all (SerpApi-only)
    # We'll record them so the caller can decide to call SerpApi.
    # (bags, max_price, sort_by, emissions, layover_duration, exclude_conns, max_duration,
    #  deep_search, show_hidden, departure_token, booking_token)
    # These are handled at the aggregate level in build_gf_urls; kept here for clarity.

    return LinkOut(url=url, coverage=cov)

# ─────────────────────────────────────────────────────────────────────────────
# Public: build_gf_urls — handles multi-airports, multi-city and coverage
# ─────────────────────────────────────────────────────────────────────────────

def build_gf_urls(
    *,
    # SerpApi core
    departure_id: Optional[str] = None,
    arrival_id: Optional[str] = None,
    outbound_date: Optional[str] = None,
    return_date: Optional[str] = None,
    type: Optional[str] = None,  # 1=Round, 2=One-way, 3=Multi
    travel_class: Optional[str] = None,  # 1..4
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0,
    # Filters
    stops: Optional[str] = None,
    include_airlines: Optional[str] = None,  # CSV or None
    exclude_airlines: Optional[str] = None,
    outbound_times: Optional[str] = None,
    return_times: Optional[str] = None,
    # Localization
    hl: str = "en",
    gl: str = "US",
    currency: str = "USD",
    # SerpApi-only / advanced — kept for coverage reporting
    deep_search: Optional[bool] = None,
    show_hidden: Optional[bool] = None,
    bags: Optional[int] = None,
    max_price: Optional[int] = None,
    sort_by: Optional[str] = None,        # 1..6 in SerpApi
    emissions: Optional[str] = None,      # 1 (less only)
    layover_duration: Optional[str] = None,  # "min,max" minutes
    exclude_conns: Optional[str] = None,  # CSV of airport codes
    max_duration: Optional[int] = None,
    departure_token: Optional[str] = None,
    booking_token: Optional[str] = None,
    # Multi-city (SerpApi-style)
    multi_city_json: Optional[str] = None,
) -> dict:
    """
    Returns:
    {
      "links": [ { "url": "...", "coverage": Coverage(...) }, ... ],
      "unmatched_global": [ ... ],   # parameters that no URL can represent
      "serpapi_fallback": { ... }    # ready-to-call SerpApi params for full fidelity
    }
    """

    cov_global_unmatched: List[str] = []

    # Detect multi-city
    if type == "3" or multi_city_json:
        # Try to encode multi-city via fast-flights.
        # If your fast-flights exposes a 'trip=multi-city' + multiple legs, this will work.
        # Otherwise, we return one URL per consecutive pair of legs (approximation) and mark unmatched.
        legs = []
        try:
            legs_in = json.loads(multi_city_json) if multi_city_json else []
            assert isinstance(legs_in, list) and legs_in, "multi_city_json must be a non-empty JSON array"
        except Exception as e:
            raise ValueError(f"Invalid multi_city_json: {e}")

        for leg in legs_in:
            d = leg.get("departure_id"); a = leg.get("arrival_id"); dt = leg.get("date")
            if not (d and a and dt):
                raise ValueError("Each multi-city leg needs departure_id, arrival_id, date")
            _validate_airport_or_place(d); _validate_airport_or_place(a); _validate_iso_date(dt)
            legs.append(dict(dep=d, arr=a, date=dt))

        # If your fast-flights supports passing an array of legs with trip='multi-city', do it:
        links = []
        try:
            # Build one multi-city TFS
            ff_legs = [FlightData(date=l["date"], from_airport=l["dep"], to_airport=l["arr"]) for l in legs]
            pax = Passengers(adults=adults, children=children, infants_in_seat=infants_in_seat, infants_on_lap=infants_on_lap)
            tfs_kwargs = dict(flight_data=ff_legs, trip="multi-city", passengers=pax)

            if travel_class in _TRAVEL_CLASS:
                tfs_kwargs["seat"] = _TRAVEL_CLASS[travel_class]
            if stops in _STOPS_MAP:
                tfs_kwargs["max_stops"] = _STOPS_MAP[stops]

            # Attempt to pass airline/time filters if supported
            for key, raw in [
                ("include_airlines", _csv_to_list(include_airlines)),
                ("exclude_airlines", _csv_to_list(exclude_airlines)),
            ]:
                if raw:
                    try:
                        TFSData.from_interface(**{**tfs_kwargs, key: raw})
                        tfs_kwargs[key] = raw
                    except TypeError:
                        cov_global_unmatched.append(f"{key} (not supported by installed fast-flights)")

            tfs = TFSData.from_interface(**tfs_kwargs).as_b64().decode()
            url = f"https://www.google.com/travel/flights?tfs={_q(tfs)}&hl={_q(hl)}&gl={_q(gl)}&curr={_q(currency)}"
            links.append(LinkOut(url=url, coverage=Coverage(encoded=["tfs","hl","gl","currency"], unmatched=[])))
            # Note: per-leg time windows for multi-city vary by library support; if needed, you can extend similarly.
        except TypeError:
            # Library can't build multi-city tfs; approximate with chained one-way URLs
            cov_global_unmatched.append("multi-city (not supported by installed fast-flights; returned per-leg URLs)")
            links = []
            for i in range(len(legs)-1):
                lo = _build_single_url(
                    dep=legs[i]["dep"], arr=legs[i]["arr"], outbound_date=legs[i]["date"],
                    return_date=None, type="2",
                    travel_class=travel_class,
                    adults=adults, children=children, infants_in_seat=infants_in_seat, infants_on_lap=infants_on_lap,
                    stops=stops,
                    include_airlines=_csv_to_list(include_airlines),
                    exclude_airlines=_csv_to_list(exclude_airlines),
                    outbound_times=None, return_times=None,
                    hl=hl, gl=gl, currency=currency,
                )
                links.append(lo)
        return {
            "links": [dict(url=l.url, coverage=l.coverage.__dict__) for l in links],
            "unmatched_global": sorted(set(cov_global_unmatched + _serpapi_only_flags(deep_search, show_hidden, bags, max_price, sort_by, emissions, layover_duration, exclude_conns, max_duration, departure_token, booking_token))),
            "serpapi_fallback": build_serpapi_params(**locals() | {"engine": "google_flights"})
        }

    # Non multi-city: handle multi-airports (CSV) → cartesian product
    deps = _csv_to_list(departure_id)
    arrs = _csv_to_list(arrival_id)
    if not deps or not arrs:
        raise ValueError("departure_id and arrival_id are required (CSV or single).")
    if not outbound_date:
        raise ValueError("outbound_date is required for non multi-city searches.")
    if type == "1" and not return_date:
        raise ValueError("return_date is required when type=1 (Round trip).")

    links: List[LinkOut] = []
    for dep, arr in itertools.product(deps, arrs):
        lo = _build_single_url(
            dep=dep, arr=arr,
            outbound_date=outbound_date,
            return_date=return_date if (type == "1" or (return_date and type is None)) else None,
            type=type,
            travel_class=travel_class,
            adults=adults, children=children, infants_in_seat=infants_in_seat, infants_on_lap=infants_on_lap,
            stops=stops,
            include_airlines=_csv_to_list(include_airlines),
            exclude_airlines=_csv_to_list(exclude_airlines),
            outbound_times=outbound_times,
            return_times=return_times,
            hl=hl, gl=gl, currency=currency,
        )
        links.append(lo)

    return {
        "links": [dict(url=l.url, coverage=l.coverage.__dict__) for l in links],
        "unmatched_global": sorted(set(_serpapi_only_flags(
            deep_search, show_hidden, bags, max_price, sort_by, emissions,
            layover_duration, exclude_conns, max_duration, departure_token, booking_token
        ))),
        "serpapi_fallback": build_serpapi_params(**locals() | {"engine": "google_flights"})
    }

# ─────────────────────────────────────────────────────────────────────────────
# SerpApi payload builder (for full fidelity or fallback)
# ─────────────────────────────────────────────────────────────────────────────

def build_serpapi_params(**kwargs) -> dict:
    """
    Return a sanitized SerpApi parameters dict from the same inputs.
    Only includes keys recognized by SerpApi; leaves out Nones and empty strings.
    """
    # Accepted SerpApi keys (superset)
    allowed = {
        "engine","departure_id","arrival_id","outbound_date","return_date",
        "hl","gl","currency","type","travel_class","adults","children",
        "infants_in_seat","infants_on_lap","stops","include_airlines","exclude_airlines",
        "bags","max_price","sort_by","emissions","layover_duration","exclude_conns",
        "max_duration","outbound_times","return_times","multi_city_json",
        "departure_token","booking_token","deep_search","show_hidden","no_cache","async","zero_trace","api_key","output","json_restrictor"
    }
    result = {}
    for k, v in kwargs.items():
        if k in allowed and v not in (None, "", []):
            result[k] = v
    # SerpApi expects CSVs as CSV strings, not arrays
    for key in ("include_airlines","exclude_airlines"):
        if isinstance(result.get(key), list):
            result[key] = ",".join(result[key])
    result.setdefault("engine", "google_flights")
    return result

# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────

def _serpapi_only_flags(
    deep_search, show_hidden, bags, max_price, sort_by, emissions,
    layover_duration, exclude_conns, max_duration, departure_token, booking_token
) -> List[str]:
    unmatched = []
    if deep_search: unmatched.append("deep_search (SerpApi-only)")
    if show_hidden: unmatched.append("show_hidden (SerpApi-only)")
    if bags not in (None, 0): unmatched.append("bags (no URL equivalent)")
    if max_price is not None: unmatched.append("max_price (no URL equivalent)")
    if sort_by is not None: unmatched.append("sort_by (no URL equivalent)")
    if emissions is not None: unmatched.append("emissions (no URL equivalent)")
    if layover_duration: unmatched.append("layover_duration (no URL equivalent)")
    if exclude_conns: unmatched.append("exclude_conns (no URL equivalent)")
    if max_duration is not None: unmatched.append("max_duration (no URL equivalent)")
    if departure_token: unmatched.append("departure_token (result-navigation, SerpApi-only)")
    if booking_token: unmatched.append("booking_token (booking step, SerpApi-only)")
    return unmatched
