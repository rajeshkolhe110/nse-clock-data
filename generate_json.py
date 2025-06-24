import requests
import json
from datetime import datetime, timedelta

YAHOO_URL = (
    "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"
    "?range=1d&interval=1m&includePrePost=false"
)

def fetch_yahoo_time():
    resp = requests.get(YAHOO_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    chart = data["chart"]["result"][0]
    timestamps = chart["timestamp"]
    if not timestamps:
        raise ValueError("No timestamps in Yahoo data")
    # Use the last timestamp in UTC
    ts = timestamps[-1]
    dt_utc = datetime.utcfromtimestamp(ts)
    # Convert to IST (UTC+5:30)
    dt_ist = dt_utc + timedelta(hours=5, minutes=30)
    return dt_ist

def main():
    try:
        dt = fetch_yahoo_time()
        time_val = dt.strftime("%d-%b-%Y %H:%M:%S")
        print("📅 Yahoo time (IST):", time_val)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch from Yahoo: {e}")

    now = datetime.now()
    open_t = dt.replace(hour=9, minute=15, second=0, microsecond=0)
    close_t = dt.replace(hour=15, minute=30, second=0, microsecond=0)

    is_open = (dt.date() == now.date()) and (open_t <= dt <= close_t)
    result = {
        "status": "OPEN" if is_open else "CLOSED",
        "last_updated": time_val
    }

    with open("market_status.json", "w") as f:
        json.dump(result, f, indent=2)

    print("✅ market_status.json updated:", result)


if __name__ == "__main__":
    main()
