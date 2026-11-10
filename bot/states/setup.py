"""Qadirdon AI — Sozlash jarayoni uchun FSM holatlar."""

from aiogram.fsm.state import State, StatesGroup


class SetupStates(StatesGroup):
    """AI sozlash bosqichlari (Setup wizard)."""

    choosing_language = State()       # Til tanlash
    choosing_role = State()           # Rol tanlash (aka, opa, ...)
    choosing_character_model = State()  # Personaj modelini tanlash (Rayhona, Kamola, ...)
    choosing_game_mode = State()        # O'yin rejimini tanlash (Story vs Classic)
    entering_name = State()           # AI ismini kiritish
    setting_personality = State()     # Xarakter/shaxsiyat belgilash
    setting_emoji_level = State()     # Emoji darajasi
    setting_typing_speed = State()    # Yozish tezligi
    confirming = State()              # Tasdiqlash
