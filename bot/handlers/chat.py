"""Qadirdon AI — Botdagi xabarlarni qayta ishlash handleri.

Foydalanuvchi botga bevosita matn yozganida, bot faqat boshqaruv/sozlama
uchun mo'ljallanganini tushuntiradi. AI bilan muloqot faqat Telegram Business
orqali shaxsiy akkauntda amalga oshiriladi.
"""

from __future__ import annotations
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.keyboards.reply import main_menu_keyboard
from config.settings import settings
from db.models import User

chat_router = Router(name="bot_message_router")

MENU_BUTTONS = {
    "⚙️ Sozlamalar",
    "📖 Kundalik",
    "📊 Statistika",
    "💰 Balans va Tariflar",
    "💎 Premium",
    "ℹ️ Yordam",
    "🔐 Admin Panel (/admin)",
    "❌ Bekor qilish",
}


@chat_router.message(
    F.chat.type == "private",
    F.text,
    ~F.text.startswith("/"),
)
async def handle_direct_bot_message(
    message: types.Message,
    user: User,
    state: FSMContext,
) -> None:
    """Bot ichida tasodifiy matn yozilganda yo'naltiruvchi xabar beradi."""
    # FSM holati mavjud bo'lsa (masalan, ism kiritish), aralashmaymiz
    current_state = await state.get_state()
    if current_state is not None:
        return

    user_text = message.text.strip()
    if user_text in MENU_BUTTONS:
        return

    is_adm = message.from_user.id in settings.admin_id_list if message.from_user else False

    info_text = (
        "ℹ️ <b>Qadirdon AI — Boshqaruv Markazi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Ushbu bot faqat AI xarakterini sozlash, profil va hisobni boshqarish uchun mo'ljallangan.\n\n"
        "🤖 <b>AI bilan qanday suhbatlashiladi?</b>\n"
        "Sun'iy intellekt sizning shaxsiy profilingizga <b>Telegram Business</b> orqali ulanadi "
        "va sizning nomingizdan insondek muloqot qiladi.\n\n"
        "📌 <i>Sozlamalarni o'zgartirish yoki statistikani ko'rish uchun quyidagi menyudan foydalaning:</i>"
    )

    await message.answer(
        info_text,
        reply_markup=main_menu_keyboard(is_admin=is_adm),
        parse_mode="HTML",
    )
