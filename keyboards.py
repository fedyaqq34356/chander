from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import CURRENCIES

def get_main_keyboard():
    """Главная клавиатура с кнопкой обмена"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Совершить обмен")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

def get_currency_keyboard():
    """Клавиатура выбора валют"""
    buttons = []
    for i in range(0, len(CURRENCIES), 2):
        row = []
        row.append(KeyboardButton(text=CURRENCIES[i]))
        if i + 1 < len(CURRENCIES):
            row.append(KeyboardButton(text=CURRENCIES[i + 1]))
        buttons.append(row)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_confirmation_keyboard():
    """Клавиатура подтверждения заявки"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подтвердить")],
            [KeyboardButton(text="Отменить")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_cancel_keyboard():
    """Клавиатура отмены"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отменить")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard