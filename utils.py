import random
import string
from datetime import datetime, timedelta
from config import EXCHANGE_RATES, SPECIAL_RATES

def generate_order_id():
    """Генерирует ID заявки"""
    return f"N{random.randint(10000000, 99999999)}"

def generate_secret():
    """Генерирует секретный код"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(12))

def calculate_exchange_amount(sell_currency, buy_currency, amount):
    """Рассчитывает сумму обмена с учетом курса"""
    sell_rate = EXCHANGE_RATES.get(sell_currency, 1.0)
    buy_rate = EXCHANGE_RATES.get(buy_currency, 1.0)
    
    # Проверяем специальные курсы
    pair_key = f"{sell_currency}-{buy_currency}"
    if pair_key in SPECIAL_RATES:
        special_rate = SPECIAL_RATES[pair_key]
        base_amount = (amount * sell_rate) / buy_rate
        return base_amount * (1 + special_rate)
    
    return (amount * sell_rate) / buy_rate

def get_expiry_time():
    """Возвращает время истечения заявки (30 минут)"""
    expiry = datetime.utcnow() + timedelta(minutes=30)
    return expiry.strftime("%H:%M UTC")

def format_order_message(sell_currency, sell_amount, buy_currency, buy_amount, order_id, secret):
    """Форматирует сообщение о заявке"""
    expiry_time = get_expiry_time()
    
    return f"""✅ Подтвердить
Ваша заявка #{order_id} принята!
Secret: `{secret}`
Продаете: {sell_amount} {sell_currency}
Покупаете: {buy_amount:.4f} {buy_currency}
Ордер актуален до {expiry_time}
Ваша заявка отправлена в обработку, ожидайте сообщение от оператора.
ОБЯЗАТЕЛЬНО! Запросите secret код для Вашей заявки у менеджера ДО проведения любых операций."""

def get_new_order_message():
    """Возвращает сообщение для создания новой заявки"""
    return """Для создания новой заявки нажмите Совершить обмен
Нажимая Совершить обмен, Вы подтверждаете что ознакомились с разделом /terms"""

def format_admin_message(username, user_id, sell_currency, sell_amount, buy_currency, buy_amount, order_id, secret):
    """Форматирует сообщение для админской группы"""
    expiry_time = get_expiry_time()
    
    return f"""Заявка #{order_id}

Secret: `{secret}`
Продажа: {sell_amount} {sell_currency}
Покупка: {buy_amount:.8f} {buy_currency}

Курс актуален до {expiry_time}

Пользователь: @{username} (ID: {user_id})"""
