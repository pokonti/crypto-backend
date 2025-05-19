from fastapi import FastAPI, Query, HTTPException
import asyncio
from typing import List
from crypto.logic import supported_currencies, cached_data, cryptos_cache, run_background_tasks, fetch_coin_chart, fetch_detailed_info
from crypto.schemas import Crypto
from fastapi.middleware.cors import CORSMiddleware
import time
from db.database import engine, Base
from auth import auth
from portfolio import portfolio
from chatbot import chatbot
app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost",
    "http://localhost:8000",
    "https://crypto-frontend-cly7.vercel.app",
    "https://crypto-frontend-cly7-pokontis-projects.vercel.app",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    asyncio.create_task(run_background_tasks())

@app.get("/crypto-prices")
def get_prices(currency: str = Query("usd", enum=supported_currencies)):
    data = cached_data.get(currency)
    if not data:
        return {"error": f"No data available for {currency.upper()} yet. Try again shortly."}
    return data


@app.get("/cryptos", response_model=List[Crypto])
async def get_cryptos():
    if not cryptos_cache:
        raise HTTPException(
            status_code=503,
            detail="Cryptocurrency data is not available yet. Please try again shortly."
        )
    return cryptos_cache


coin_cache = {}
coin_data_cache = {}
@app.get("/chart/{coin_id}")
async def get_coin_chart(coin_id: str, vs_currency: str = "usd", days: int = 7):
    current_time = time.time()

    if coin_id in coin_cache and current_time - coin_cache[coin_id]['timestamp'] < 1200:
        return coin_cache[coin_id]['data']
    data = fetch_coin_chart(coin_id, vs_currency, days)

    coin_cache[coin_id] = {
        "data": data,
        "timestamp": current_time
    }
    return data

@app.get("/{coin_id}")
async def get_coin(coin_id: str):
    current_time = time.time()

    if coin_id in coin_data_cache and current_time - coin_data_cache[coin_id]['timestamp'] < 1200:
        return coin_data_cache[coin_id]['data']
    data = fetch_detailed_info(coin_id)

    coin_data_cache[coin_id] = {
        "data": data,
        "timestamp": current_time
    }
    return data

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(chatbot.router)