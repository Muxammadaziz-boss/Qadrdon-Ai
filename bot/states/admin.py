"""Qadirdon AI — Admin paneli uchun FSM holatlar."""

from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Admin kabineti bosqichlari."""

    waiting_for_user_id_for_balance = State()  # Pul qo'shish uchun User ID kutish
    waiting_for_amount = State()               # Qo'shiladigan summani kutish

    waiting_for_user_id_for_plan = State()     # Obuna berish uchun User ID kutish

    waiting_for_user_id_search = State()       # Foydalanuvchini qidirish uchun ID kutish

    waiting_for_broadcast_text = State()       # E'lon matnini kutish
    confirm_broadcast = State()                # E'lonni tasdiqlash

