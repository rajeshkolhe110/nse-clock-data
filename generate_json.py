import requests
import json
import sys
from datetime import datetime, timedelta

YAHOO_URL = (
    "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"
    "?range=1d&interval=1m&includePrePost=false"
)

def fetch_yahoo_time():
    resp = requests.get(YAHOO_URL, timeout=10)
    if resp.status_code == 429:
        # Rate-limited
        print("⚠️ Yahoo returned 429 Too Many Requests — skipping update.")
        return None
    resp.raise_for_status()
    data = resp.json()
    timestamps = data["chart"]["result"][0]["timestamp"]
    if not timestamps:
        raise ValueError("No timestamps in Yahoo response")
    # Last timestamp is UTC seconds
    ts = timestamps[-1]
    dt_utc = datetime.utcfromtimestamp(ts)
    return dt_utc + timedelta(hours=5, minutes=30)  # IST

def main():
    try:
        dt_ist = fetch_yahoo_time()
        if dt_ist is None:
            # No update, exit cleanly
            sys.exit(0)

        time_val = dt_ist.strftime("%d-%b-%Y %H:%M:%S")
        print("📅 Yahoo time (IST):", time_val)

        now = datetime.now()
        open_t = dt_ist.replace(hour=9, minute=15, second=0, microsecond=0)
        close_t = dt_ist.replace(hour=15, minute=30, second=0, microsecond=0)

        is_open = (dt_ist.date() == now.date()) and (open_t <= dt_ist <= close_t)
        result = {
            "status": "OPEN" if is_open else "CLOSED",
            "last_updated": time_val
        }

        with open("market_status.json", "w") as f:
            json.dump(result, f, indent=2)

        print("✅ market_status.json updated:", result)

    except Exception as e:
        # On any other error, skip update but exit 0
        print(f"⚠️ Update skipped due to error: {e}")
        sys.exit(0)

if __name__ == "__main__":
    main()
