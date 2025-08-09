import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional

class UTMManager:
    def __init__(self):
        # Словарь для хранения активных UTM кодов
        # Структура: {utm_code: {"type": "demo/real", "created_at": datetime, "expires_at": datetime}}
        self.active_utm_codes: Dict[str, dict] = {}
    
    def generate_utm_code(self, link_type: str) -> str:
        """Генерирует UTM код и сохраняет его с типом и временем истечения"""
        # Генерируем случайный UTM код из 12 символов
        utm_code = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        # Устанавливаем время создания и истечения (24 часа)
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(hours=24)
        
        # Сохраняем информацию о коде
        self.active_utm_codes[utm_code] = {
            "type": link_type,
            "created_at": created_at,
            "expires_at": expires_at
        }
        
        return utm_code
    
    def check_utm_code(self, utm_code: str) -> Optional[str]:
        """Проверяет UTM код и возвращает его тип (demo/real) или None если недействителен"""
        if utm_code not in self.active_utm_codes:
            return None
        
        utm_info = self.active_utm_codes[utm_code]
        
        # Проверяем, не истек ли срок действия
        if datetime.utcnow() > utm_info["expires_at"]:
            # Удаляем истекший код
            del self.active_utm_codes[utm_code]
            return None
        
        return utm_info["type"]
    
    def cleanup_expired_codes(self):
        """Очищает истекшие UTM коды"""
        current_time = datetime.utcnow()
        expired_codes = [
            code for code, info in self.active_utm_codes.items()
            if current_time > info["expires_at"]
        ]
        
        for code in expired_codes:
            del self.active_utm_codes[code]
    
    def get_active_codes_info(self) -> str:
        """Возвращает информацию об активных кодах"""
        if not self.active_utm_codes:
            return "Активных UTM кодов нет"
        
        info = "Активные UTM коды:\n\n"
        for code, data in self.active_utm_codes.items():
            expires_str = data["expires_at"].strftime("%d.%m.%Y %H:%M UTC")
            info += f"Код: {code}\nТип: {data['type']}\nИстекает: {expires_str}\n\n"
        
        return info

# Глобальный экземпляр менеджера
utm_manager = UTMManager()