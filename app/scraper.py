import time
import json
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
from datetime import datetime

# Define supported sources and their price element selectors
SOURCES = {
    "xau": {
        "url": "https://www.exchangerates.org.uk/commodities/live-gold-prices/XAU-USD.html",
        "selector": "div#p_XAUUSD",
    },
    "xag": {
        "url": "https://www.exchangerates.org.uk/commodities/live-silver-prices/XAG-USD.html",
        "selector": "div#p_XAGUSD",
    },
    "btc": {
        "url": "https://www.exchangerates.org.uk/crypto-currencies/bitcoin-price-in-us-dollar-today-btc-usd",
        "selector": "div#p_BTCUSD",
    },
}


def get_price(page, source_key: str) -> float | None:
    """
    Fetches the latest price for the given source key (xau, xag, btc)
    Returns the numeric price (float) or None if not found.
    """
    if source_key.lower() not in SOURCES:
        print(f"❌ Unsupported source '{source_key}'. Valid: {list(SOURCES.keys())}")
        return None

    src = SOURCES[source_key.lower()]
    url, selector = src["url"], src["selector"]

    try:
        page.goto(url, wait_until="networkidle", timeout=15000)
        element = page.wait_for_selector(selector, timeout=10000)
        text = element.inner_text().strip()
        numeric = float(text.replace(",", ""))
        return numeric
    except PWTimeoutError:
        print(f"❌ Timeout while waiting for selector {selector} on {url}")
        return None
    except ValueError as e:
        print(f"❌ Could not parse price text: '{text}' - {e}")
        return None
    except Exception as e:
        print(f"❌ Error fetching {source_key.upper()} price: {e}")
        return None


def fetch_all_prices():
    """
    Fetches all prices using a single browser instance.
    Returns a dict with keys: xau, xag, btc
    """
    prices = {}

    try:
        with sync_playwright() as p:
            # Launch with K8s-friendly args for containerized environments
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-dev-shm-usage',  # Overcome limited resource problems
                    '--no-sandbox',              # Required for running as root in containers
                    '--disable-setuid-sandbox',  # Required for running as root in containers
                    '--disable-gpu',             # Not needed in headless mode
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                ]
            )
            page = browser.new_page()

            for asset in SOURCES.keys():
                price = get_price(page, asset)
                if price is not None:
                    prices[asset] = price
                    print(f"✅ Fetched {asset.upper()} Price: {price}")

            browser.close()
    except Exception as e:
        print(f"❌ Failed to fetch prices: {e}")
        import traceback
        traceback.print_exc()

    return prices


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
        new_prices = fetch_all_prices()

        if new_prices:
            current_prices.update(new_prices)
            for asset, price in new_prices.items():
                print(f"✅ Updated {asset.upper()} Price: {price} at {datetime.utcnow()}")
            save_prices(current_prices)
        else:
            print("❌ Failed to fetch any prices")

        time.sleep(20)
