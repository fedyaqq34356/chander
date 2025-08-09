import random
import string
from datetime import datetime, timedelta
from config import EXCHANGE_RATES, SPECIAL_RATES
from crypto_api import CryptoAPI
from config import CRYPTO_API_KEY

# Создаем экземпляр API
crypto_api = CryptoAPI(CRYPTO_API_KEY)

def generate_order_id():
    """Генерирует ID заявки"""
    return f"N{random.randint(10000000, 99999999)}"

def generate_secret():
    """Генерирует секретный код"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(12))

async def update_rates():
    """Обновляет курсы валют через API"""
    try:
        new_rates = await crypto_api.get_crypto_rates()
        if new_rates:
            # Обновляем глобальные курсы
            EXCHANGE_RATES.update(new_rates)
            return True
    except Exception as e:
        print(f"Ошибка обновления курсов: {e}")
    return False

async def calculate_exchange_amount(sell_currency, buy_currency, amount):
    """Рассчитывает сумму обмена с учетом курса"""
    # Сначала попытаемся обновить курсы
    await update_rates()
    
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

def format_order_message(sell_currency, sell_amount, buy_currency, buy_amount, order_id, secret, is_demo=False):
    """Форматирует сообщение о заявке"""
    expiry_time = get_expiry_time()
    
    demo_warning = ""
    if is_demo:
        demo_warning = "🎭 ДЕМО ЗАЯВКА\n"
    
    return f"""{demo_warning}✅ Подтвердить
Ваша заявка #{order_id} принята!
Secret: `{secret}`
Продаете: {sell_amount} {sell_currency}
Покупаете: {buy_amount:.4f} {buy_currency}
Ордер актуален до {expiry_time}
Ваша заявка отправлена в обработку, ожидайте сообщение от оператора.
ОБЯЗАТЕЛЬНО! Запросите secret код для Вашей заявки у менеджера ДО проведения любых операций.{' (ДЕМО)' if is_demo else ''}"""

def format_admin_message(username, user_id, sell_currency, sell_amount, buy_currency, buy_amount, order_id, secret, is_demo=False):
    """Форматирует сообщение для админской группы"""
    expiry_time = get_expiry_time()
    
    demo_prefix = "🎭 ДЕМО " if is_demo else ""
    
    return f"""{demo_prefix}Заявка #{order_id}

Secret: `{secret}`
Продажа: {sell_amount} {sell_currency}
Покупка: {buy_amount:.8f} {buy_currency}

Курс актуален до {expiry_time}

Пользователь: @{username} (ID: {user_id}){' [ДЕМО РЕЖИМ]' if is_demo else ''}"""
# Добавить эту функцию в utils.py

def get_new_order_message():
    """Возвращает сообщение для создания новой заявки"""
    return """Для создания новой заявки нажмите Совершить обмен
Нажимая Совершить обмен, Вы подтверждаете что ознакомились с разделом /terms"""
