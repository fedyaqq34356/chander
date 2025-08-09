import aiohttp
import asyncio
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CryptoAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.api-ninjas.com/v1/cryptoprice"
        self.headers = {"X-Api-Key": api_key}
        
    async def get_price(self, symbol: str) -> Optional[float]:
        """Получает текущую цену для символа"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}?symbol={symbol}"
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data.get('price', 0))
                    else:
                        logger.error(f"API Error: {response.status} for symbol {symbol}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    async def get_crypto_rates(self) -> Dict[str, float]:
        """Получает курсы всех криптовалют относительно USDT"""
        rates = {}
        
        # Список пар для получения курсов (все к USDT)
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LTCUSDT", "TRXUSDT"]
        
        # USDT всегда равен 1
        rates["USDT"] = 1.0
        
        # Получаем курсы асинхронно
        tasks = []
        for symbol in symbols:
            tasks.append(self.get_price(symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error for {symbols[i]}: {result}")
                continue
                
            if result is not None:
                # Извлекаем название валюты из символа (BTCUSDT -> BTC)
                currency = symbols[i].replace('USDT', '')
                rates[currency] = result
        
        return rates