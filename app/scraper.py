import time
import json
import urllib.request
from datetime import datetime

def fetch_price():
    try:
        req = urllib.request.Request(
            "https://api.gold-api.com/price/XAU",
            headers={"Cache-Control": "no-cache"}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return float(data.get("price"))
    except Exception:
        return None

def save_price(price):
    with open("/app/price.json", "w") as f:
        json.dump({"price": price}, f)

def start_scraper():
    while True:
        price = fetch_price()
        if price is not None:
            save_price(price)
            print(f"✅ Updated Price: {price} at {datetime.utcnow()}")
        else:
            print("❌ Failed to fetch price.")
        time.sleep(20)
