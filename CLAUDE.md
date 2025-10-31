# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XAU-API is a real-time commodity price scraper and API service built with FastAPI and Playwright. It continuously scrapes XAU/USD (gold), XAG/USD (silver), and BTC/USD prices from exchangerates.org.uk and exposes them via authenticated REST endpoints.

## Architecture

### Process Model

The application runs two concurrent processes managed by `start.sh`:

1. **Scraper Process** (`app/scraper.py`): Background worker that fetches prices every 10 seconds
2. **API Process** (`app/api.py`): FastAPI server on port 8000

The scraper runs independently and auto-restarts if it crashes (monitored by start.sh). Both processes communicate via a shared file (`/app/price.json`).

### Data Flow

1. Scraper launches headless Chromium browser via Playwright
2. Navigates to exchangerates.org.uk pages for each asset (XAU, XAG, BTC)
3. Waits for specific price element selectors (e.g., `div#p_XAUUSD`)
4. Extracts and parses numeric price from element text
5. Writes all prices to `/app/price.json` atomically
6. API endpoints read from this file on each request

### Key Implementation Details

- **Price Storage**: File-based IPC via `/app/price.json` (not in-memory or database)
- **Browser Automation**: Uses Playwright with headless Chromium (single browser instance per scrape cycle)
- **Price Sources**:
  - XAU: https://www.exchangerates.org.uk/commodities/live-gold-prices/XAU-USD.html
  - XAG: https://www.exchangerates.org.uk/commodities/live-silver-prices/XAG-USD.html
  - BTC: https://www.exchangerates.org.uk/crypto-currencies/bitcoin-price-in-us-dollar-today-btc-usd
- **Authentication**: Simple API key via `X-API-Key` header (configured in `.env`)
- **Timezone**: Hard-coded to Asia/Kuala_Lumpur in Dockerfile
- **Element Selectors**: `div#p_XAUUSD`, `div#p_XAGUSD`, `div#p_BTCUSD`

## Development Commands

### Local Development

```bash
# Install dependencies
pip3 install --break-system-packages -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set up environment
cp .env.example .env
# Edit .env and set your API_KEY

# Run scraper (terminal 1)
python3 -c "from app.scraper import start_scraper; start_scraper()"

# Run API server (terminal 2)
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

### Docker

```bash
# Build image
docker build -t xau-api .

# Run container
docker run -d --restart always -p 8085:8000 --env-file .env xau-api

# View logs
docker logs -f <container-id>
```

### Testing Endpoints

```bash
# Set your API key
export API_KEY="your-key-here"

# Health check (no auth)
curl http://localhost:8000/health

# Get XAU price
curl -H "X-API-Key: $API_KEY" http://localhost:8000/price

# Get BTC price
curl -H "X-API-Key: $API_KEY" http://localhost:8000/btc-price

# Get XAG price
curl -H "X-API-Key: $API_KEY" http://localhost:8000/xag-price
```

## Deployment

The project uses GitHub Actions to automatically build and push Docker images to DockerHub on pushes to `main` or `develop` branches. Images are tagged with both `:latest` and `:<git-sha>`.

Repository: `exrienz/xau-api`

## Important Notes

- Price updates occur every 10 seconds (configurable in `app/scraper.py:103`)
- The `/app/price.json` path is hard-coded throughout - changing it requires updates in both scraper.py and api.py
- If scraping fails, the previous prices remain available until new data arrives
- The scraper prints status to stdout with emoji indicators (✅ for success, ❌ for errors)
- All price endpoints return 404 if the specific price is not available yet
- Playwright requires `--break-system-packages` flag for pip install in the Docker container
- Browser automation adds overhead - each scrape cycle launches/closes a Chromium instance
- Timeouts are set to 15s for page load and 10s for element selectors
