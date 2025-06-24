import json
from datetime import datetime
import os

STATE_FILE = "market_state.tmp"
JSON_FILE = "market_status.json"

def get_next_status():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            current = f.read().strip()
        next_status = "CLOSED" if current == "OPEN" else "OPEN"
    else:
        next_status = "OPEN"
    with open(STATE_FILE, "w") as f:
        f.write(next_status)
    return next_status

def main():
    new_status = get_next_status()
    now = datetime.now()
    formatted_time = now.strftime("%d-%b-%Y %H:%M:%S")
    utc_time = now.utcnow().isoformat() + "Z"

    data = {
        "status": new_status,
        "last_updated": formatted_time,
        "_updated_at": utc_time
    }

    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Updated {JSON_FILE} → {new_status} at {formatted_time}")

if __name__ == "__main__":
    main()
