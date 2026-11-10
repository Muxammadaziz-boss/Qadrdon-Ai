"""Qadirdon AI — Admin paneli klaviaturalari."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Admin kabineti asosiy menyusi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Umumiy Statistika", callback_data="admin:stats"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💰 Foydalanuvchi hisobini to'ldirish",
                    callback_data="admin:add_balance",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💎 To'g'ridan-to'g'ri Obuna berish",
                    callback_data="admin:give_plan",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Foydalanuvchi qidirish",
                    callback_data="admin:find_user",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📢 Barchaga xabar yuborish (Broadcast)",
                    callback_data="admin:broadcast",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Admin paneldan chiqish",
                    callback_data="admin:exit",
                ),
            ],
        ]
    )


def admin_plans_keyboard(target_user_id: int) -> InlineKeyboardMarkup:
    """Foydalanuvchiga tarif tanlash klaviaturasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🥉 Standard (30 kun)",
                    callback_data=f"admin_plan:standard:{target_user_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🥈 Premium (30 kun)",
                    callback_data=f"admin_plan:premium:{target_user_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🥇 Ultra VIP (30 kun)",
                    callback_data=f"admin_plan:ultra:{target_user_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data="admin:cancel",
                ),
            ],
        ]
    )


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    """Bekor qilish inline tugmasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish", callback_data="admin:cancel"
                ),
            ],
        ]
    )


def admin_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Broadcast xabarni tasdiqlash klaviaturasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha, yuborilsin!", callback_data="broadcast:confirm"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish", callback_data="admin:cancel"
                ),
            ],
        ]
    )

