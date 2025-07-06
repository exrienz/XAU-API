import time
import json
import urllib.request
from datetime import datetime

ASSETS = ["XAU", "XAG", "BTC"]


def fetch_price(asset: str):
    try:
        req = urllib.request.Request(
            f"https://api.gold-api.com/price/{asset}",
            headers={"Cache-Control": "no-cache"},
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return float(data.get("price"))
    except Exception:
        return None


def load_prices() -> dict:
    try:
        with open("/app/price.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_prices(prices: dict) -> None:
    with open("/app/price.json", "w") as f:
        json.dump(prices, f)


def start_scraper():
    while True:
        prices = load_prices()
        for asset in ASSETS:
            price = fetch_price(asset)
            if price is not None:
                prices[asset.lower()] = price
                print(
                    f"✅ Updated {asset} Price: {price} at {datetime.utcnow()}"
                )
            else:
                print(f"❌ Failed to fetch {asset} price.")
        save_prices(prices)
        time.sleep(20)
