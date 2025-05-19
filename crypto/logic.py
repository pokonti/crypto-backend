import asyncio
import requests
from crypto.schemas import Crypto, CryptoInfo

exchange_rates = {"usd_to_kzt": 0}
cached_data = {}
supported_currencies = ["usd", "eur", "kzt"]
cryptos_cache = []
CACHE_TIMEOUT = 60


def fetch_exchange_rate():
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD")
        if response.status_code == 200:
            data = response.json()
            kzt_rate = data["rates"]["KZT"]
            exchange_rates["usd_to_kzt"] = kzt_rate
            print(f"Updated USD→KZT rate: {kzt_rate}")
        else:
            print(f"Failed to fetch exchange rate, status: {response.status_code}")
    except Exception as e:
        print("Error fetching exchange rate:", e)

def fetch_crypto_data_kzt():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/coins/markets", params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 30,
            "page": 1,
            "sparkline": False
        })

        if response.ok:
            data = response.json()
            cached_data["usd"] = {coin["id"]: {"usd": coin["current_price"]} for coin in data}
            usd_to_kzt = exchange_rates["usd_to_kzt"]
            cached_data["kzt"] = {
                coin["id"]: {"kzt": round(coin["current_price"] * usd_to_kzt, 2)}
                for coin in data
            }
            print("Crypto prices updated")
        else:
            print("API Error:", response.status_code)

    except Exception as e:
        print("Error fetching crypto data:", e)


def fetch_cryptos():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        limit = 30
        # USD prices
        params_usd = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
        }
        response_usd = requests.get(url, params=params_usd)

        # EUR prices
        params_eur = {
            "vs_currency": "eur",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
        }
        response_eur = requests.get(url, params=params_eur)

        if response_usd.status_code == 200 and response_eur.status_code == 200:
            data_usd = response_usd.json()
            data_eur = response_eur.json()

            cryptos = []

            for crypto_usd, crypto_eur in zip(data_usd, data_eur):
                if crypto_usd["id"] == crypto_eur["id"]:
                    cryptos.append(Crypto(
                        id=crypto_usd["id"],
                        logo=crypto_usd['image'],
                        name=crypto_usd['name'],
                        symbol=crypto_usd['symbol'],
                        price_dollars=crypto_usd['current_price'],
                        price_euros=crypto_eur['current_price'],
                        change_24h=crypto_usd['price_change_percentage_24h']
                    ))

            return cryptos
    except Exception as e:
        print(f"Error fetching cryptos: {e}")



def fetch_coin_chart(coin_id: str, vs_currency: str, days: int):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days
    }
    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()

    except Exception as e:
        print(f"Error fetching crypto chart: {e}")

def fetch_detailed_info(coin_id: str):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            description = data.get("description", {}).get("en", "")
            whitepaper = data.get("links", {}).get("whitepaper")
            market_data = data.get("market_data", {})
            current_price = market_data.get("current_price", {})

            return CryptoInfo(
                description=description,
                whitepaper=whitepaper,
                currency=current_price.get("usd", 0),
                price_change_percentage_24h=market_data.get("price_change_percentage_24h", 0),
                price_change_percentage_7d=market_data.get("price_change_percentage_7d", 0),
                price_change_percentage_14d=market_data.get("price_change_percentage_14d", 0),
                price_change_percentage_30d=market_data.get("price_change_percentage_30d", 0),
                price_change_percentage_60d=market_data.get("price_change_percentage_60d", 0),
                price_change_percentage_200d=market_data.get("price_change_percentage_200d", 0),
                price_change_percentage_1y=market_data.get("price_change_percentage_1y", 0),
            )

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "An unexpected error occurred."}


async def run_background_tasks():
    while True:
        fetch_exchange_rate()
        fetch_crypto_data_kzt()

        new_cryptos = fetch_cryptos()

        if new_cryptos:
            cryptos_cache.clear()
            cryptos_cache.extend(new_cryptos)
            # print(f"Updated cryptos cache with {len(new_cryptos)} items")

        await asyncio.sleep(CACHE_TIMEOUT)


def fetch_price_for_portfolio(coin_id:str) :
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # current_price_usd = data["market_data"]["current_price"]["usd"]
            return data.get("market_data", {}).get("current_price", {}).get("usd")

    except Exception as e:
        print(f"Error fetching price data: {e}")


