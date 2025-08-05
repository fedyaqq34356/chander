from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import AdminStates
from config import ADMIN_GROUP_ID, EXCHANGE_RATES, CURRENCIES

router = Router()

def is_admin_group(message: Message) -> bool:
    """Проверяет, что сообщение из админской группы"""
    return str(message.chat.id) == ADMIN_GROUP_ID

@router.message(Command("send"), F.chat.id.in_([int(ADMIN_GROUP_ID)] if ADMIN_GROUP_ID else []))
async def send_command(message: Message, state: FSMContext):
    """Команда /send для отправки сообщения пользователю"""
    if not is_admin_group(message):
        return
    
    parts = message.text.split(' ', 2)
    if len(parts) < 3:
        await message.answer("Использование: /send <user_id> <сообщение>")
        return
    
    try:
        user_id = int(parts[1])
        text = parts[2]
        
        await message.bot.send_message(user_id, text)
        await message.answer(f"Сообщение отправлено пользователю {user_id}")
        
    except ValueError:
        await message.answer("Некорректный ID пользователя")
    except Exception as e:
        await message.answer(f"Ошибка отправки: {e}")

@router.message(Command("kyrs"), F.chat.id.in_([int(ADMIN_GROUP_ID)] if ADMIN_GROUP_ID else []))
async def rates_command(message: Message):
    """Команда /kyrs для просмотра и изменения курсов"""
    if not is_admin_group(message):
        return
    
    parts = message.text.split()
    
    if len(parts) == 1:
        # Показать текущие курсы
        rates_text = "Текущие курсы обмена:\n\n"
        for currency, rate in EXCHANGE_RATES.items():
            rates_text += f"{currency}: {rate}\n"
        
        rates_text += "\nДля изменения курса используйте:\n/kyrs <валюта> <новый_курс>"
        await message.answer(rates_text)
        
    elif len(parts) == 3:
        # Изменить курс
        currency = parts[1].upper()
        try:
            new_rate = float(parts[2])
            
            if currency in CURRENCIES:
                EXCHANGE_RATES[currency] = new_rate
                await message.answer(f"Курс {currency} изменен на {new_rate}")
            else:
                await message.answer(f"Валюта {currency} не поддерживается")
                
        except ValueError:
            await message.answer("Некорректное значение курса")
    else:
        await message.answer("Использование: /kyrs [валюта] [новый_курс]")

@router.message(Command("help"), F.chat.id.in_([int(ADMIN_GROUP_ID)] if ADMIN_GROUP_ID else []))
async def help_command(message: Message):
    """Команда /help для админов"""
    if not is_admin_group(message):
        return
    
    help_text = """Доступные команды администратора:

/send <user_id> <сообщение> - отправить сообщение пользователю
/kyrs - посмотреть текущие курсы
/kyrs <валюта> <курс> - изменить курс валюты
/help - показать эту справку

Поддерживаемые валюты: """ + ", ".join(CURRENCIES)
    
    await message.answer(help_text)