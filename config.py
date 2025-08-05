import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")  # ID админской группы

# Поддерживаемые криптовалюты
CURRENCIES = ["BTC", "ETH", "USDT", "SOL", "LTC", "TRX"]

# Курсы обмена (по умолчанию)
EXCHANGE_RATES = {
    "BTC": 45000.0,
    "ETH": 2500.0,
    "USDT": 1.0,
    "SOL": 100.0,
    "LTC": 70.0,
    "TRX": 0.1
}

# Комиссия для пары USDT-BTC: -5%
SPECIAL_RATES = {
    "USDT-BTC": -0.05
}