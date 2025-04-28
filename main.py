import asyncio
from fastapi import FastAPI, Query, HTTPException
from typing import List
from logic import supported_currencies, cached_data, cryptos_cache, run_background_tasks, fetch_coin_chart, \
    chat_with_gemini, CACHE_TIMEOUT, fetch_detailed_info
from models import Crypto, PromptRequest, CryptoInfo
from fastapi.middleware.cors import CORSMiddleware
import time
app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost",
    "http://localhost:8000",
    "https://crypto-frontend-cly7.vercel.app"
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
def get_coin_chart(coin_id: str, vs_currency: str = "usd", days: int = 7):
    current_time = time.time()

    if coin_id in coin_cache and current_time - coin_cache[coin_id]['timestamp'] < CACHE_TIMEOUT:
        return coin_cache[coin_id]['data']
    data = fetch_coin_chart(coin_id, vs_currency, days)

    coin_cache[coin_id] = {
        "data": data,
        "timestamp": current_time
    }
    return data

@app.get("/{coin_id}")
def get_coin(coin_id: str, response_model=CryptoInfo):
    current_time = time.time()

    if coin_id in coin_data_cache and current_time - coin_data_cache[coin_id]['timestamp'] < CACHE_TIMEOUT:
        return coin_data_cache[coin_id]['data']
    data = fetch_detailed_info(coin_id)

    coin_data_cache[coin_id] = {
        "data": data,
        "timestamp": current_time
    }
    return data


@app.post("/chat")
async def chat(request: PromptRequest):
    return {"response": chat_with_gemini(request.prompt)}


# @app.get("/test-updates")
# async def test_updates():
#     fetch_exchange_rate()
#     fetch_crypto_data_kzt()
#     fetch_cryptos()
#
#     fetch_exchange_rate()
#     fetch_crypto_data_kzt()
#     fetch_cryptos()
#
#     return {
#         "exchange_rate": exchange_rates,
#         "crypto_data": bool(cached_data),
#         "cryptos_cache": len(cryptos_cache)
#     }