from gfurl import build_gf_url

url = build_gf_url(
    legs=[{"from":"SYD","to":"MEL","date":"2025-08-15"},
          {"from":"MEL","to":"SYD","date":"2025-08-20"}],
    pax={"adults":1,"children":0,"infants_in_seat":0,"infants_on_lap":0},
    cabin="ECONOMY",           # PREMIUM_ECONOMY|BUSINESS|FIRST
    stops="NONSTOP",           # ANY|NONSTOP|MAX_1|MAX_2
    include_airlines=["QF"],   # or alliances: ["STAR_ALLIANCE"] etc.
    dep_time_window=(6,18),    # 06:00–18:00
    arr_time_window=None,
    hl="en", gl="AU", currency="AUD"
)
# -> "https://www.google.com/travel/flights?tfs=...&hl=en&gl=AU&curr=AUD"
print(f"🔗 Generated URL: {url}")