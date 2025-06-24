import requests
import json
from datetime import datetime

# Single session for the primary endpoint
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
    "Accept-Language": "en-US,en;q=0.9"
})

def fetch_nifty_time():
    # --- Primary: official API ---
    try:
        session.get("https://www.nseindia.com", timeout=10)
        main_url = (
            "https://www.nseindia.com/api/equity-stockIndices"
            "?index=NIFTY%2050"
        )
        resp = session.get(main_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if data and "timeVal" in data[0]:
                print("✅ Fetched from primary NSE API")
                return data[0]["timeVal"]
    except Exception as e:
        print("⚠️ Primary API failed:", e)

    # --- Fallback: archives.nseindia.com ---
    try:
        archive_url = (
            "https://archives.nseindia.com/live_market/"
            "dynaContent/live_watch/stock_watch/"
            "niftyStockWatch.json"
        )
        print("🔄 Trying fallback:", archive_url)
        fallback = requests.get(archive_url, timeout=10)
        fallback.raise_for_status()
        arr = fallback.json()
        if "time" in arr:
            print("✅ Fetched from archives mirror")
            return arr["time"]
        else:
            raise ValueError("No 'time' field in archive response")
    except Exception as e:
        raise RuntimeError(f"Both endpoints failed: {e}")

def main():
    time_val = fetch_nifty_time()  # May raise if both fail
    print("📅 NSE time:", time_val)

    now = datetime.now()
    dt = datetime.strptime(time_val, "%d-%b-%Y %H:%M:%S")
    open_t = datetime.strptime("09:15:00", "%H:%M:%S").time()
    close_t = datetime.strptime("15:30:00", "%H:%M:%S").time()

    is_open = (dt.date() == now.date()) and (open_t <= dt.time() <= close_t)
    result = {
        "status": "OPEN" if is_open else "CLOSED",
        "last_updated": time_val
    }

    with open("market_status.json", "w") as f:
        json.dump(result, f, indent=2)

    print("✅ market_status.json updated:", result)

if __name__ == "__main__":
    main()
