"""Qadirdon AI — Til tanlash handleri.

Foydalanuvchi tilni tanlaydi va keyingi bosqichga (rol) o'tadi.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy import update

from bot.keyboards.inline import role_keyboard
from bot.states.setup import SetupStates
from db.models import User
from db.session import async_session

setup_language_router = Router(name="setup_language")

# ── Til nomlari ──────────────────────────────────────────────────────────────
LANGUAGE_NAMES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}


@setup_language_router.callback_query(
    SetupStates.choosing_language,
    F.data.startswith("lang:"),
)
async def on_language_chosen(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    """
    Til tanlash callback'ini qayta ishlaydi.
    Handles the language selection callback.
    """
    await callback.answer()

    lang_code = callback.data.split(":")[1]  # uz, ru, en
    lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)

    # Bazada tilni saqlash / Save language to DB
    async with async_session() as session:
        stmt = update(User).where(User.id == user.id).values(language=lang_code)
        await session.execute(stmt)
        await session.commit()

    # FSM data'ga saqlash
    await state.update_data(language=lang_code)

    # Keyingi bosqich — rol tanlash / Next step — role selection
    text = (
        f"✅ Til tanlandi: <b>{lang_name}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎭 <b>Endi AI rolini tanlang:</b>\n\n"
        "AI sizga qanday munosabatda bo'lishini belgilang.\n"
        "Har bir rol o'ziga xos gaplashish uslubiga ega:\n\n"
        "👨 <b>Aka</b> — Katta aka, himoyachi va maslahatchi\n"
        "👦 <b>Uka</b> — Kichik uka, samimiy va quvnoq\n"
        "👩 <b>Opa</b> — Katta opa, g'amxo'r va mehribon\n"
        "👧 <b>Singil</b> — Kichik singil, erka va yoqimtoy\n"
        "🤱 <b>Ona</b> — Ona, har doim tushunadi va qo'llaydi\n"
        "💕 <b>Qiz do'st</b> — Romantik va samimiy suyukli yor\n"
        "💍 <b>Ayol / Turmush o'rtog'i</b> — Ro'zg'or, oila va vafoli suyukli rafiqa"
    )
    await callback.message.edit_text(
        text,
        reply_markup=role_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(SetupStates.choosing_role)
