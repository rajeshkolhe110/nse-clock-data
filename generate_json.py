import requests
import json
from datetime import datetime

# ————————————————
# Step A: Try the official NSE API
# ————————————————

def fetch_from_primary():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9"
    })

    # 1) hit homepage to get cookies
    session.get("https://www.nseindia.com", timeout=10)
    # 2) fetch index JSON
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if not data or "timeVal" not in data[0]:
        raise ValueError("No timeVal in primary NSE response")
    print("✅ Fetched from primary NSE API")
    return data[0]["timeVal"]


# ————————————————
# Step B: Fallback to the “archives” mirror
# ————————————————

def fetch_from_archive():
    url = (
      "https://archives.nseindia.com/live_market/"
      "dynaContent/live_watch/stock_watch/"
      "niftyStockWatch.json"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    arr = resp.json()
    if "time" not in arr:
        raise ValueError("No 'time' field in archive response")
    print("✅ Fetched from archives mirror")
    return arr["time"]


# ————————————————
# Step C: Orchestrate & write JSON
# ————————————————

def main():
    # Try primary, else archive, else fail
    try:
        time_val = fetch_from_primary()
    except Exception as e1:
        print("⚠️ Primary API failed:", e1)
        try:
            time_val = fetch_from_archive()
        except Exception as e2:
            raise RuntimeError(f"Both endpoints failed:\n • {e1}\n • {e2}")

    print("📅 NSE time:", time_val)

    # Determine OPEN vs CLOSED
    now = datetime.now()
    dt = datetime.strptime(time_val, "%d-%b-%Y %H:%M:%S")
    open_t = datetime.strptime("09:15:00", "%H:%M:%S").time()
    close_t = datetime.strptime("15:30:00", "%H:%M:%S").time()

    is_open = (dt.date() == now.date()) and (open_t <= dt.time() <= close_t)
    result = {
        "status": "OPEN" if is_open else "CLOSED",
        "last_updated": time_val
    }

    # Write out the JSON file
    with open("market_status.json", "w") as f:
        json.dump(result, f, indent=2)

    print("✅ market_status.json updated:", result)


if __name__ == "__main__":
    main()
