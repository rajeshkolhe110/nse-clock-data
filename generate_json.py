import requests
import json
from datetime import datetime

# Use a requests session to avoid Cloudflare blocks
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
    "Accept-Language": "en-US,en;q=0.9"
})

def fetch_nifty_time():
    # 1) Hit homepage to get cookies
    session.get("https://www.nseindia.com", timeout=10)
    # 2) Fetch NIFTY 50 index JSON
    url = (
      "https://www.nseindia.com/api/equity-stockIndices"
      "?index=NIFTY%2050"
    )
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if not data:
        raise ValueError("No data in NSE response")
    return data[0]["timeVal"]  # e.g. "24-Jun-2025 11:26:00"

def main():
    time_val = fetch_nifty_time()
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
