"""
build_gf_url.py
───────────────
Generate a Google-Flights search link from structured user input.

Re    # ── 4. Report any SerpApi extras we couldn't express  ───────────────────
    unmatched = []
    if deep_search:
        unmatched.append("deep_search")
    if show_hidden:
        unmatched.append("show_hidden")
    if include_airlines:
        unmatched.append("include_airlines (not supported by fast-flights)")
    if exclude_airlines:
        unmatched.append("exclude_airlines (not supported by fast-flights)")
    if dep_time_window:
        unmatched.append("dep_time_window (not supported by fast-flights)")
    if arr_time_window:
        unmatched.append("arr_time_window (not supported by fast-flights)")    pip install fast-flights==2.*  # MIT-licensed helper that handles the tfs protobuf
"""
from __future__ import annotations
import base64
import datetime as _dt
from typing import List, Literal, Optional, Sequence

from fast_flights.filter import TFSData           # → builds the protobuf → base64
from fast_flights.flights_impl import FlightData  # typed leg helper
from fast_flights.flights_impl import Passengers  # typed pax helper

# ──────────────────────────────────────────────────────────────────────────────
# Public interface
# ──────────────────────────────────────────────────────────────────────────────
def build_gf_url(
    *,
    legs: Sequence[dict],                    # [{"from":"SYD","to":"MEL","date":"2025-08-15"}, …]
    pax: dict,                               # {"adults":1,"children":0,"infants_in_seat":0,"infants_on_lap":0}
    cabin: Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"] = "ECONOMY",
    stops: Literal["ANY", "NONSTOP", "MAX_1", "MAX_2"] = "ANY",
    include_airlines: Optional[Sequence[str]] = None,   # ["QF"] or alliances
    exclude_airlines: Optional[Sequence[str]] = None,   # ["UA"]
    dep_time_window: Optional[tuple[int, int]] = None,  # (startHr, endHr)
    arr_time_window: Optional[tuple[int, int]] = None,
    hl: str = "en",
    gl: str = "US",
    currency: str = "USD",
    # SerpApi-only switches that do *not* affect Google’s URL ↴
    deep_search: bool = False,
    show_hidden: bool = False,
) -> dict:
    """
    Returns {
        "url": "<fully-formed Google Flights link>",
        "coverage": {"tfs": [...fulfilled fields…], "unmatched": [...SerpApi fields you asked for but tfs can’t encode…]}
    }
    """
    # ── 1. SerpApi ⇢ Google field mapping ───────────────────────────────────
    leg_objs: List[FlightData] = []
    for leg in legs:
        _validate_airport(leg["from"])
        _validate_airport(leg["to"])
        _validate_date(leg["date"])
        leg_objs.append(
            FlightData(
                date=leg["date"],
                from_airport=leg["from"],
                to_airport=leg["to"],
                # fast-flights also lets you pass dep/arr hour filters per leg if needed
            )
        )

    seat_map = {
        "ECONOMY": "economy",
        "PREMIUM_ECONOMY": "premium-economy",
        "BUSINESS": "business",
        "FIRST": "first",
    }

    trip_type = (
        "one-way"
        if len(leg_objs) == 1
        else "round-trip"
        if len(leg_objs) == 2 and leg_objs[0].from_airport == leg_objs[1].to_airport
        else "multi-city"
    )

    pax_obj = Passengers(
        adults=pax.get("adults", 1),
        children=pax.get("children", 0),
        infants_in_seat=pax.get("infants_in_seat", 0),
        infants_on_lap=pax.get("infants_on_lap", 0),
    )

    # Google only supports *max stops* (0,1,2) in the protobuf
    stops_map = {
        "ANY": None,
        "NONSTOP": 0,
        "MAX_1": 1,
        "MAX_2": 2,
    }
    max_stops = stops_map[stops]

    # ── 2. Build the protobuf & encode to tfs ────────────────────────────────
    # Note: fast-flights library only supports basic parameters in from_interface
    tfs_filter = TFSData.from_interface(
        flight_data=leg_objs,
        trip=trip_type,
        passengers=pax_obj,
        seat=seat_map[cabin],
        max_stops=max_stops,
    )
    tfs_b64 = tfs_filter.as_b64().decode()

    # ── 3. Compose the URL  ──────────────────────────────────────────────────
    params = {
        "tfs": tfs_b64,
        "hl": hl,
        "gl": gl,
        "curr": currency,
    }
    # canonical Google URL
    url = "https://www.google.com/travel/flights?" + "&".join(f"{k}={_escape(v)}" for k, v in params.items())

    # ── 4. Report any SerpApi extras we couldn’t express  ───────────────────
    unmatched = []
    if deep_search:
        unmatched.append("deep_search")
    if show_hidden:
        unmatched.append("show_hidden")
    if arr_time_window and len(arr_time_window) == 2 and dep_time_window is None:
        # Google needs dep window to carry arrival … so warn
        unmatched.append("arr_time_window (departure-only provided)")

    return {
        "url": url,
        "coverage": {"tfs": list(params.keys()), "unmatched": unmatched},
    }


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────
import re, urllib.parse as _u

_IATA_RE = re.compile(r"^[A-Z0-9]{3}$")


def _validate_airport(code: str) -> None:
    if not _IATA_RE.match(code):
        raise ValueError(f"'{code}' is not a valid IATA/ICAO airport code")


def _validate_date(iso_date: str) -> None:
    try:
        _dt.date.fromisoformat(iso_date)
    except ValueError as e:
        raise ValueError(f"Invalid date '{iso_date}': {e}")


def _escape(v: str) -> str:
    return _u.quote_plus(v, safe="")  # Google expects URL-safe base64


# ───────────────────────────── example usage ────────────────────────────────
if __name__ == "__main__":
    url_obj = build_gf_url(
        legs=[
            {"from": "SYD", "to": "MEL", "date": "2025-08-15"},
            {"from": "MEL", "to": "SYD", "date": "2025-08-20"},
        ],
        pax={"adults": 1},
        cabin="ECONOMY",
        stops="NONSTOP",
        include_airlines=["QF"],
        dep_time_window=(6, 18),
        hl="en",
        gl="AU",
        currency="AUD",
    )
    print("🔗", url_obj["url"])
    print("Coverage ➜", url_obj["coverage"])
