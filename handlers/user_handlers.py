from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import ExchangeStates
from keyboards import (
    get_main_keyboard, 
    get_currency_keyboard, 
    get_confirmation_keyboard,
    get_cancel_keyboard
)
from utils import (
    calculate_exchange_amount,
    generate_order_id,
    generate_secret,
    format_order_message,
    format_admin_message,
    get_new_order_message
)
from config import CURRENCIES, ADMIN_GROUP_ID

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    """Обработчик команды /start"""
    text = """Для создания новой заявки нажмите Совершить обмен
Нажимая Совершить обмен, Вы подтверждаете что ознакомились с разделом /terms"""
    
    await message.answer(text, reply_markup=get_main_keyboard())

@router.message(Command("terms"))
async def terms_handler(message: Message):
    """Обработчик команды /terms"""
    terms_text = """Правила обмена криптовалют:
1. Обязательства сторон: Создавая заявку, вы соглашаетесь с условиями обмена и подтверждаете, что владеете отправляемыми средствами на законных основаниях.
2. Сроки исполнения: Обработка заявок занимает до 30 минут с момента подтверждения транзакции в сети. Задержки возможны из-за загруженности блокчейна.
3. Курс обмена: Фиксируется на момент создания заявки и не подлежит изменению.
4. Комиссии: Все комиссии блокчейна оплачивает отправитель. Дополнительные комиссии сервиса удерживаются из суммы обмена.
5. Ошибки в данных: Ответственность за корректность введенных реквизитов несет пользователь. Ошибки в данных могут привести к потере средств.
6. Антифрод-политика: Запрещены операции с нелегальными источниками средств. Подозрительные транзакции передаются в компетентные органы.
7. Отмена заявки: Заявки после отправки средств отмене не подлежат.
8. Поддержка: По всем вопросам обращайтесь в службу поддержки.

Создавая заявку, вы подтверждаете свое согласие с данными условиями."""
    
    await message.answer(terms_text)

@router.message(F.text == "Совершить обмен")
async def start_exchange(message: Message, state: FSMContext):
    """Начало процесса обмена"""
    await message.answer("Выберите монету, которую хотите обменять", 
                        reply_markup=get_currency_keyboard())
    await state.set_state(ExchangeStates.choosing_sell_currency)

@router.message(ExchangeStates.choosing_sell_currency, F.text.in_(CURRENCIES))
async def choose_sell_currency(message: Message, state: FSMContext):
    """Выбор валюты для продажи"""
    await state.update_data(sell_currency=message.text)
    await message.answer("Введите количество, которое хотите обменять", 
                        reply_markup=get_cancel_keyboard())
    await state.set_state(ExchangeStates.entering_amount)

@router.message(ExchangeStates.entering_amount)
async def enter_amount(message: Message, state: FSMContext):
    """Ввод суммы обмена"""
    if message.text == "Отменить":
        await cancel_operation(message, state)
        return
    
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("Введите положительное число")
            return
        
        await state.update_data(sell_amount=amount)
        await message.answer("Выберите валюту, которую хотите получить", 
                            reply_markup=get_currency_keyboard())
        await state.set_state(ExchangeStates.choosing_buy_currency)
        
    except ValueError:
        await message.answer("Введите корректное число")

@router.message(ExchangeStates.choosing_buy_currency, F.text.in_(CURRENCIES))
async def choose_buy_currency(message: Message, state: FSMContext):
    """Выбор валюты для покупки"""
    data = await state.get_data()
    sell_currency = data['sell_currency']
    sell_amount = data['sell_amount']
    buy_currency = message.text
    
    if sell_currency == buy_currency:
        await message.answer("Нельзя обменять валюту саму на себя. Выберите другую валюту.")
        return
    
    buy_amount = calculate_exchange_amount(sell_currency, buy_currency, sell_amount)
    
    await state.update_data(
        buy_currency=buy_currency,
        buy_amount=buy_amount
    )
    
    await message.answer("💱")
    
    confirmation_text = f"""Подтвердите заявку:
Продаете: {sell_amount} {sell_currency}
Покупаете: {buy_amount:.4f} {buy_currency}"""
    
    await message.answer(confirmation_text, reply_markup=get_confirmation_keyboard())
    await state.set_state(ExchangeStates.confirming_order)

@router.message(ExchangeStates.confirming_order, F.text == "Подтвердить")
async def confirm_order(message: Message, state: FSMContext):
    """Подтверждение заявки"""
    data = await state.get_data()
    
    order_id = generate_order_id()
    secret = generate_secret()
    
    # Отправляем сообщение пользователю
    user_message = format_order_message(
        data['sell_currency'],
        data['sell_amount'],
        data['buy_currency'],
        data['buy_amount'],
        order_id,
        secret
    )
    
    await message.answer(user_message, parse_mode="Markdown")
    
    # Отправляем второе сообщение с предложением новой заявки
    new_order_message = get_new_order_message()
    await message.answer(new_order_message, reply_markup=get_main_keyboard())
    
    # Отправляем в админскую группу
    if ADMIN_GROUP_ID:
        admin_message = format_admin_message(
            message.from_user.username or "unknown",
            message.from_user.id,
            data['sell_currency'],
            data['sell_amount'],
            data['buy_currency'],
            data['buy_amount'],
            order_id,
            secret
        )
        
        try:
            await message.bot.send_message(ADMIN_GROUP_ID, admin_message, parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка отправки в админскую группу: {e}")
    
    await state.clear()

@router.message(ExchangeStates.confirming_order, F.text == "Отменить")
async def cancel_order(message: Message, state: FSMContext):
    """Отмена заявки"""
    await cancel_operation(message, state)

async def cancel_operation(message: Message, state: FSMContext):
    """Отмена операции"""
    await message.answer("Операция отменена", reply_markup=get_main_keyboard())
    await state.clear()

@router.message(F.text == "Отменить")
async def cancel_handler(message: Message, state: FSMContext):
    """Общий обработчик отмены"""
    await cancel_operation(message, state)
