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


def _read_prices() -> dict:
    with open("/app/price.json", "r") as f:
        return json.load(f)


def _authorize(request: Request) -> None:
    client_api_key = request.headers.get("X-API-Key")
    if client_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@app.get("/price")
async def get_price(request: Request):
    _authorize(request)
    try:
        data = _read_prices()
        price = data.get("xau")
        if price is None:
            raise FileNotFoundError
        return JSONResponse(content={"price": price})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Price not available yet.")


@app.get("/btc-price")
async def get_btc_price(request: Request):
    _authorize(request)
    try:
        data = _read_prices()
        price = data.get("btc")
        if price is None:
            raise FileNotFoundError
        return JSONResponse(content={"price": price})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Price not available yet.")


@app.get("/xag-price")
async def get_xag_price(request: Request):
    _authorize(request)
    try:
        data = _read_prices()
        price = data.get("xag")
        if price is None:
            raise FileNotFoundError
        return JSONResponse(content={"price": price})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Price not available yet.")


@app.get("/health")
async def health_check():
    try:
        data = _read_prices()
        return JSONResponse(
            content={
                "status": "ok",
                "last_price": {
                    "xau": data.get("xau"),
                    "xag": data.get("xag"),
                    "btc": data.get("btc"),
                },
            }
        )
    except FileNotFoundError:
        return JSONResponse(content={"status": "error", "last_price": None})
