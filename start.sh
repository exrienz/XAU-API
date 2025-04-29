#!/bin/bash
start_scraper() {
  echo "Starting scraper..."
  python3 -u -c "from app.scraper import start_scraper; start_scraper()" &
  SCRAPER_PID=$!
}
start_scraper
uvicorn app.api:app --host 0.0.0.0 --port 8000 &
API_PID=$!
while true; do
  if ! kill -0 $SCRAPER_PID > /dev/null 2>&1; then
    echo "⚠️ Scraper crashed! Restarting..."
    start_scraper
  fi
  sleep 5
done
