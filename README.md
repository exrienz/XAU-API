# XAU Server - Real-Time Gold Price API.
A lightweight real-time price scraper and API service.
## Features
- Scrapes live XAU/USD, XAG/USD and BTC prices every 20 seconds
- Serves price over protected FastAPI endpoint
- Health check endpoint (`/health`) to monitor scraper liveness
- Auto-restarts scraper if it crashes
- Dockerized for easy deployment
- Persistent file-based price sharing
## Usage
1. Clone this repository.
2. Copy `.env.example` to `.env` and set your `API_KEY`.
3. Build and run:
```bash
docker build -t xau-api .
docker run -d --restart always -p 8085:8000 --env-file .env xau-api
```
## API Endpoints
- `GET /price` — Requires `X-API-Key` header. Returns latest XAU/USD price.
- `GET /btc-price` — Requires `X-API-Key` header. Returns latest BTC price.
- `GET /xag-price` — Requires `X-API-Key` header. Returns latest XAG/USD price.
- `GET /health` — No auth. Shows service health status including all prices.
## License
MIT License
