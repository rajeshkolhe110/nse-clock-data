import requests
import json
import sys
from datetime import datetime, timedelta

# 1-minute chart for ^NSEI (NIFTY 50)
YAHOO_URL = (
    "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"
    "?range=1d&interval=1m&includePrePost=false"
)

# Fallback mirror
ARCHIVE_URL = (
    "https://archives.nseindia.com/live_market/"
    "dynaContent/live_watch/stock_watch/"
    "niftyStockWatch.json"
)

def fetch_yahoo_time():
    resp = requests.get(YAHOO_URL, timeout=10)
    if resp.status_code == 429:
        print("⚠️ Yahoo returned 429 Too Many Requests — falling back.")
        return None
    resp.raise_for_status()
    data = resp.json()
    timestamps = data["chart"]["result"][0]["timestamp"]
    if not timestamps:
        raise ValueError("No timestamps in Yahoo response")
    # Last timestamp is in UTC seconds
    ts = timestamps[-1]
    dt_utc = datetime.utcfromtimestamp(ts)
    return dt_utc + timedelta(hours=5, minutes=30)  # convert to IST

def fetch_archive_time():
    resp = requests.get(ARCHIVE_URL, timeout=10)
    resp.raise_for_status()
    arr = resp.json()
    if "time" not in arr:
        raise ValueError("No 'time' field in archive response")
    # time is already in "DD-MMM-YYYY HH:MM:SS" IST
    return datetime.strptime(arr["time"], "%d-%b-%Y %H:%M:%S")

def main():
    # Try Yahoo first
    try:
        dt_ist = fetch_yahoo_time()
    except Exception as e:
        print("⚠️ Yahoo fetch failed:", e)
        dt_ist = None

    # If Yahoo skipped or failed, try archive
    if dt_ist is None:
        try:
            print("🔄 Trying archives mirror")
            dt_ist = fetch_archive_time()
        except Exception as e:
            print("⚠️ Archive fetch failed:", e)
            print("⚠️ Both endpoints failed — skipping update.")
            sys.exit(0)

    time_val = dt_ist.strftime("%d-%b-%Y %H:%M:%S")
    print("📅 Market timestamp (IST):", time_val)

    # Determine market open/closed (09:15–15:30 IST)
    now = datetime.now()
    open_t = dt_ist.replace(hour=9, minute=15, second=0, microsecond=0)
    close_t = dt_ist.replace(hour=15, minute=30, second=0, microsecond=0)
    is_open = (dt_ist.date() == now.date()) and (open_t <= dt_ist <= close_t)

    result = {
        "status": "OPEN" if is_open else "CLOSED",
        "last_updated": time_val,
        # Always-changing field to force Git diff & commit
        "_updated_at": datetime.utcnow().isoformat() + "Z"
    }

    with open("market_status.json", "w") as f:
        json.dump(result, f, indent=2)

    print("✅ market_status.json updated:", result)

if __name__ == "__main__":
    main()
