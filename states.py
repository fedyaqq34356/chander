from aiogram.fsm.state import State, StatesGroup

class ExchangeStates(StatesGroup):
    choosing_sell_currency = State()
    entering_amount = State()
    choosing_buy_currency = State()
    confirming_order = State()

class AdminStates(StatesGroup):
    sending_message = State()
    setting_rates = State()