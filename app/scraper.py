import time
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

SYMBOL_MAP = {
    "XAU": "XAUUSD",
    "XAG": "XAGUSD", 
    "BTC": "BTCUSD"
}


def fetch_octafx_prices():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        
        cache_buster = int(time.time() * 1000)
        url = f"https://www.octafx.com/markets/quotes/mt5/?_={cache_buster}"
        
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "lxml")
        prices = {}
        
        for table in soup.find_all("table"):
            thead = table.find("thead")
            if thead:
                cols = [th.get_text(strip=True) for th in thead.find_all("th")]
            else:
                first = table.find("tr")
                cols = [cell.get_text(strip=True) for cell in first.find_all(["th","td"])]
            
            body = table.find("tbody") or table
            for tr in body.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["th","td"])]
                if len(cells) == len(cols):
                    row = dict(zip(cols, cells))
                    symbol = row.get("Symbol", "")
                    bid = row.get("Bid", "")
                    
                    for asset, symbol_name in SYMBOL_MAP.items():
                        if symbol == symbol_name and bid:
                            try:
                                prices[asset.lower()] = float(bid)
                            except ValueError:
                                continue
        
        return prices
    except Exception as e:
        print(f"❌ Failed to fetch OctaFX prices: {e}")
        return {}


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
        current_prices = load_prices()
        new_prices = fetch_octafx_prices()
        
        if new_prices:
            current_prices.update(new_prices)
            for asset, price in new_prices.items():
                print(f"✅ Updated {asset.upper()} Price: {price} at {datetime.utcnow()}")
            save_prices(current_prices)
        else:
            print("❌ Failed to fetch any prices from OctaFX")
        
        time.sleep(10)
