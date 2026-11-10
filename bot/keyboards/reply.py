"""Qadirdon AI — Reply (oddiy) klaviaturalar."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi."""
    keyboard = [
        [
            KeyboardButton(text="⚙️ Sozlamalar"),
            KeyboardButton(text="📊 Statistika"),
        ],
        [
            KeyboardButton(text="💰 Balans va Tariflar"),
            KeyboardButton(text="ℹ️ Yordam"),
        ],
    ]

    # Agar admin bo'lsa, maxsus tugma qo'shiladi
    if is_admin:
        keyboard.append([KeyboardButton(text="🔐 Admin Panel (/admin)")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish klaviaturasi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
