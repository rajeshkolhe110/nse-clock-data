import json
from datetime import datetime

def main():
    now = datetime.now()
    ist_time_str = now.strftime("%d-%b-%Y %H:%M:%S")
    utc_time_str = datetime.utcnow().isoformat() + "Z"

    data = {
        "status": "OPEN" if 9 <= now.hour < 15 else "CLOSED",
        "last_updated": ist_time_str,
        "_updated_at": utc_time_str
    }

    print("✅ Writing market_status.json with:", data)

    with open("market_status.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
