from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from pathlib import Path
import json

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("API_KEY")
app = FastAPI()

@app.get("/price")
async def get_price(request: Request):
    client_api_key = request.headers.get("X-API-Key")
    if client_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    try:
        with open("/app/price.json", "r") as f:
            data = json.load(f)
            return JSONResponse(content={"price": data["price"]})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Price not available yet.")

@app.get("/health")
async def health_check():
    try:
        with open("/app/price.json", "r") as f:
            data = json.load(f)
            return JSONResponse(content={"status": "ok", "last_price": data["price"]})
    except FileNotFoundError:
        return JSONResponse(content={"status": "error", "last_price": None})
