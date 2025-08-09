from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import AdminStates
from config import ADMIN_GROUP_ID, EXCHANGE_RATES, CURRENCIES
from utm_manager import utm_manager

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

@router.message(Command("demolink"), F.chat.id.in_([int(ADMIN_GROUP_ID)] if ADMIN_GROUP_ID else []))
async def generate_demo_link(message: Message):
    """Генерирует демо-ссылку"""
    if not is_admin_group(message):
        return
    
    try:
        # Получаем username бота
        bot_info = await message.bot.get_me()
        bot_username = bot_info.username
        
        # Генерируем UTM код для демо
        utm_code = utm_manager.generate_utm_code("demo")
        
        # Создаем ссылку
        demo_link = f"https://t.me/{bot_username}?start={utm_code}"
        
        await message.answer(
            f"🔗 Demo ссылка сгенерирована:\n\n"
            f"`{demo_link}`\n\n"
            f"📅 Действует 24 часа\n"
            f"🎭 Тип: ДЕМО режим\n"
            f"🔑 UTM код: `{utm_code}`",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await message.answer(f"Ошибка генерации демо-ссылки: {e}")

@router.message(Command("reallink"), F.chat.id.in_([int(ADMIN_GROUP_ID)] if ADMIN_GROUP_ID else []))
async def generate_real_link(message: Message):
    """Генерирует реальную ссылку"""
    if not is_admin_group(message):
        return
    
    try:
        # Получаем username бота
        bot_info = await message.bot.get_me()
        bot_username = bot_info.username
        
        # Генерируем UTM код для реального режима
        utm_code = utm_manager.generate_utm_code("real")
        
        # Создаем ссылку
        real_link = f"https://t.me/{bot_username}?start={utm_code}"
        
        await message.answer(
            f"🔗 Real ссылка сгенерирована:\n\n"
            f"`{real_link}`\n\n"
            f"📅 Действует 24 часа\n"
            f"💰 Тип: РЕАЛЬНЫЙ режим\n"
            f"🔑 UTM код: `{utm_code}`",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await message.answer(f"Ошибка генерации реальной ссылки: {e}")

@router.message(Command("links"), F.chat.id.in_([int(ADMIN_GROUP_ID)] if ADMIN_GROUP_ID else []))
async def show_active_links(message: Message):
    """Показывает активные UTM ссылки"""
    if not is_admin_group(message):
        return
    
    # Очищаем истекшие коды
    utm_manager.cleanup_expired_codes()
    
    # Получаем информацию об активных кодах
    info = utm_manager.get_active_codes_info()
    
    # Создаем инлайн-клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Создать Demo ссылку", callback_data="generate_demo"),
            InlineKeyboardButton(text="Создать Real ссылку", callback_data="generate_real")
        ]
    ])
    
    await message.answer(f"📋 {info}", reply_markup=keyboard)

@router.callback_query(F.data.in_(["generate_demo", "generate_real"]))
async def process_link_generation(callback: CallbackQuery):
    """Обрабатывает нажатие на кнопки генерации ссылок"""
    if not is_admin_group(callback.message):
        await callback.answer("Эта команда доступна только в админской группе")
        return
    
    try:
        # Получаем username бота
        bot_info = await callback.message.bot.get_me()
        bot_username = bot_info.username
        
        # Определяем тип ссылки
        link_type = "demo" if callback.data == "generate_demo" else "real"
        
        # Генерируем UTM код
        utm_code = utm_manager.generate_utm_code(link_type)
        
        # Создаем ссылку
        link = f"https://t.me/{bot_username}?start={utm_code}"
        link_type_display = "ДЕМО" if link_type == "demo" else "РЕАЛЬНЫЙ"
        
        await callback.message.answer(
            f"🔗 {link_type_display} ссылка сгенерирована:\n\n"
            f"`{link}`\n\n"
            f"📅 Действует 24 часа\n"
            f"{'🎭' if link_type == 'demo' else '💰'} Тип: {link_type_display} режим\n"
            f"🔑 UTM код: `{utm_code}`",
            parse_mode="Markdown"
        )
        await callback.answer()
        
    except Exception as e:
        await callback.message.answer(f"Ошибка генерации ссылки: {e}")
        await callback.answer()

@router.message(Command("help"), F.chat.id.in_([int(ADMIN_GROUP_ID)] if ADMIN_GROUP_ID else []))
async def help_command(message: Message):
    """Команда /help для админов"""
    if not is_admin_group(message):
        return
    
    help_text = """Доступные команды администратора:

/send <user_id> <сообщение> - отправить сообщение пользователю
/kyrs - посмотреть текущие курсы
/kyrs <валюта> <курс> - изменить курс валюты

🔗 UTM ссылки:
/links - открыть меню управления ссылками

/help - показать эту справку

Поддерживаемые валюты: """ + ", ".join(CURRENCIES)
    
    await message.answer(help_text)
