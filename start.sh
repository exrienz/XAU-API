#!/bin/bash
set -e

echo "🚀 Starting XAU-API services..."

# Trap signals for graceful shutdown
trap 'echo "🛑 Shutting down..."; kill $SCRAPER_PID $API_PID 2>/dev/null; exit 0' SIGTERM SIGINT

start_scraper() {
  echo "📊 Starting scraper process..."
  python3 -u -c "from app.scraper import start_scraper; start_scraper()" &
  SCRAPER_PID=$!
  echo "✅ Scraper started with PID $SCRAPER_PID"
}

start_api() {
  echo "🌐 Starting API server..."
  uvicorn app.api:app --host 0.0.0.0 --port 8000 &
  API_PID=$!
  echo "✅ API server started with PID $API_PID"
}

# Start both services
start_scraper
start_api

# Monitor both processes
while true; do
  # Check scraper
  if ! kill -0 $SCRAPER_PID > /dev/null 2>&1; then
    echo "⚠️ Scraper crashed! Restarting..."
    start_scraper
  fi

  # Check API server
  if ! kill -0 $API_PID > /dev/null 2>&1; then
    echo "⚠️ API server crashed! Restarting..."
    start_api
  fi

  sleep 5
done
