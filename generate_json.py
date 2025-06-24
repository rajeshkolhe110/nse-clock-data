import requests
import json
import sys
from datetime import datetime, timedelta

YAHOO_URL = (
    "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI"
    "?range=1d&interval=1m&includePrePost=false"
)
ARCHIVE_URL = (
    "https://archives.nseindia.com/live_market/"
    "dynaContent/live_watch/stock_watch/"
    "niftyStockWatch.json"
)

def fetch_yahoo_time():
    resp = requests.get(YAHOO_URL, timeout=10)
    if resp.status_code == 429:
        print("⚠️ Yahoo rate-limited — falling back")
        return None
    resp.raise_for_status()
    data = resp.json()
    timestamps = data["chart"]["result"][0]["timestamp"]
    if not timestamps:
        raise ValueError("Yahoo JSON missing timestamps")
    ts = timestamps[-1]
    return datetime.utcfromtimestamp(ts) + timedelta(hours=5, minutes=30)

def fetch_archive_time():
    resp = requests.get(ARCHIVE_URL, timeout=10)
    resp.raise_for_status()
    arr = resp.json()
    if "time" not in arr:
        raise ValueError("Archive JSON missing time field")
    return datetime.strptime(arr["time"], "%d-%b-%Y %H:%M:%S")

def main():
    dt = fetch_yahoo_time()
    if dt is None:
        try:
            print("🔄 Using archive fallback")
            dt = fetch_archive_time()
        except Exception as e:
            print("⚠️ Both endpoints failed — skip update", e)
            sys.exit(0)

    time_str = dt.strftime("%d-%b-%Y %H:%M:%S")
    now = datetime.now()
    open_time = dt.replace(hour=9, minute=15, second=0, microsecond=0)
    close_time = dt.replace(hour=15, minute=30, second=0, microsecond=0)
    is_open = (dt.date() == now.date()) and (open_time <= dt <= close_time)

    result = {
        "status": "OPEN" if is_open else "CLOSED",
        "last_updated": time_str,
        "_updated_at": datetime.utcnow().isoformat() + "Z"
    }

    with open("market_status.json", "w") as f:
        json.dump(result, f, indent=2)

    print("✅ market_status.json updated:", result)

if __name__ == "__main__":
    main()
