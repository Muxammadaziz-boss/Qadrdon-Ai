"""Qadirdon AI — Sozlamalarni o'zgartirish FSM holatlari."""

from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    """Mavjud sozlamalarni alohida tahrirlash holatlari."""

    editing_name = State()
    editing_personality = State()

