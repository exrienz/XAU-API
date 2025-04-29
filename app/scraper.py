import re
import subprocess
import time
import json
from datetime import datetime

def fetch_curl_output():
    try:
        url = f"https://r.jina.ai/primexbt.com/price-chart/currencies/xau-usd?nocache={int(time.time())}"
        result = subprocess.run(
            ["curl", "-s", "-H", "Cache-Control: no-cache", url],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def extract_price(text):
    match = re.search(r"XAU\s*/\s*USD\s*=+\s*([\d,]+\.\d+)", text, re.MULTILINE)
    if match:
        return float(match.group(1).replace(',', ''))
    return None

def save_price(price):
    with open("/app/price.json", "w") as f:
        json.dump({"price": price}, f)

def start_scraper():
    while True:
        content = fetch_curl_output()
        if content:
            price = extract_price(content)
            if price:
                save_price(price)
                print(f"✅ Updated Price: {price} at {datetime.utcnow()}")
            else:
                print("❌ Could not find XAU/USD price.")
        else:
            print("❌ Failed to fetch content.")
        time.sleep(20)
