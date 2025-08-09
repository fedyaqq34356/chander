import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")  # ID админской группы

# API ключ для криптовалютных данных
CRYPTO_API_KEY = "AOW+eS2+9pydgA2vqULxIA==BrNtGI6blyrTpUbE"

# Поддерживаемые криптовалюты
CURRENCIES = ["BTC", "ETH", "USDT", "SOL", "LTC", "TRX"]


async def fetch_price(session, symbol):
    url = f"https://api.api-ninjas.com/v1/cryptoprice?symbol={symbol}USDT"
    headers = {"X-Api-Key": CRYPTO_API_KEY}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return symbol, float(data.get("price", 0))
        return symbol, None


async def load_exchange_rates():
    rates = {"USDT": 1.0}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price(session, cur) for cur in CURRENCIES if cur != "USDT"]
        results = await asyncio.gather(*tasks)
    for currency, price in results:
        if price is not None:
            rates[currency] = price
    return rates


# Загружаем актуальные курсы прямо при старте
EXCHANGE_RATES = asyncio.run(load_exchange_rates())

# Комиссия для пары USDT-BTC: -5%
SPECIAL_RATES = {
    "USDT-BTC": -0.05
}
