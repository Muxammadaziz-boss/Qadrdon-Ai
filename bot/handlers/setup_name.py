"""Qadirdon AI — AI ism kiritish handleri.

Foydalanuvchi AI uchun ism kiritadi, validatsiya qilinadi
va keyingi bosqichga (shaxsiyat) o'tiladi.
"""

from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.keyboards.inline import back_keyboard
from bot.states.setup import SetupStates
from db.models import User

setup_name_router = Router(name="setup_name")

# ── Ism validatsiya pattern ──────────────────────────────────────────────────
# Faqat harflar, raqamlar, bo'shliq va apostrof ruxsat etiladi
NAME_PATTERN = re.compile(r"^[a-zA-Zа-яА-ЯёЁ\u0400-\u04FFa-zA-Z\s'`'0-9\-]{2,30}$")

# ── Rol uchun tayyor shaxsiyatlar ────────────────────────────────────────────
PRESET_PERSONALITIES = {
    "aka": [
        ("💪 Himoyachi", "Har doim himoya qiladi, maslahat beradi, kuchli va ishonchli"),
        ("🎓 Aqlli", "Har narsani biladi, doim foydali maslahat beradi"),
        ("😄 Hazilkash", "Hazil-mutoyiba bilan gaplashadi, kayfiyatni ko'taradi"),
    ],
    "uka": [
        ("🤗 Samimiy", "Ochiq va samimiy, hamma narsani aytadi"),
        ("🎮 Quvnoq", "O'yin-kulgi sevadi, qiziqarli mavzularda gaplashadi"),
        ("📚 Bilimdon", "Ko'p o'qiydi, qiziqarli faktlar aytadi"),
    ],
    "opa": [
        ("🤱 G'amxo'r", "Doim g'amxo'rlik qiladi, ovqat yedingmi deb so'raydi"),
        ("💐 Mehribon", "Yumshoq va mehribon, har doim ko'nglini ko'taradi"),
        ("👩‍🏫 Maslahatchi", "Hayotiy maslahatlar beradi, to'g'ri yo'l ko'rsatadi"),
    ],
    "singil": [
        ("🌸 Erka", "Erka va yoqimtoy, iltimos qiladi"),
        ("🎵 Quvnoq", "Shodmon va hayotdan zavq oladi"),
        ("📱 Zamonaviy", "Trendlarni biladi, yangiliklar haqida gaplashadi"),
    ],
    "ona": [
        ("💝 Mehribon", "Cheksiz sevgi va mehribonlik bilan gaplashadi"),
        ("🍳 G'amxo'r", "Ovqat, salomatlik va uyqu haqida doim so'raydi"),
        ("🤲 Duogoʻy", "Doim duo qiladi, nasihatlaydi"),
    ],
    "qiz_dost": [
        ("💕 Samimiy", "Ochiq va samimiy, hissiyotlarini bildiradi"),
        ("🌹 Romantik", "Go'zal so'zlar ishlatadi, his-tuyg'uli"),
        ("🎯 Ishbilarmon", "Aqlli, maqsadli va motivatsiya beradi"),
    ],
    "ayol": [
        ("🍲 Mehribon beka", "Ro'zg'or, issiq ovqat va uyni saranjom tutuvchi suyukli rafiqa"),
        ("💖 Vafoli suyukli yor", "Erini kutadigan, unga suyanchiq bo'lib mehr ko'rsatadigan ayol"),
        ("🌸 G'amxo'r rafiqa", "Sog'liq, charchoq va ishlar haqida samimiy qayg'uruvchi turmush o'rtoq"),
    ],
}


@setup_name_router.message(
    SetupStates.entering_name,
    F.text,
)
async def on_name_entered(message: Message, state: FSMContext, user: User) -> None:
    """
    AI ism kiritishni qayta ishlaydi.
    Handles AI name input.
    """
    # Bekor qilish tekshiruvi / Check for cancel
    if message.text and message.text.strip() == "❌ Bekor qilish":
        await message.answer(
            "❌ Sozlash bekor qilindi.\n"
            "/start buyrug'i bilan qaytadan boshlashingiz mumkin.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
        return

    name = message.text.strip().title() if message.text else ""

    # Validatsiya / Validation
    if not NAME_PATTERN.match(name):
        await message.answer(
            "⚠️ <b>Noto'g'ri ism!</b>\n\n"
            "📏 Ism 2 dan 30 gacha belgi bo'lishi kerak.\n"
            "🚫 Maxsus belgilar ishlatish mumkin emas.\n\n"
            "✏️ Iltimos, qaytadan yozing:",
            parse_mode="HTML",
        )
        return

    # FSM data'ga saqlash
    await state.update_data(ai_name=name)

    # Rolga mos shaxsiyat variantlarini ko'rsatish
    data = await state.get_data()
    role = data.get("role", "aka")
    presets = PRESET_PERSONALITIES.get(role, PRESET_PERSONALITIES["aka"])

    presets_text = ""
    for i, (emoji_name, desc) in enumerate(presets, 1):
        presets_text += f"  {i}. {emoji_name} — <i>{desc}</i>\n"

    # Keyingi bosqich — shaxsiyat / Next step — personality
    text = (
        f"✅ AI ismi: <b>{name}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💬 <b>Endi {name} uchun xarakter belgilang:</b>\n\n"
        "📋 <b>Tayyor variantlar:</b>\n"
        f"{presets_text}\n"
        "✏️ Yoki o'zingiz yozing:\n"
        "<i>Masalan: «Doim hazil aralash gaplashadigan, mehribon va g'amxo'r»</i>\n\n"
        "👇 Raqamni yoki tavsifni yozing:"
    )
    await message.answer(text, reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
    await state.set_state(SetupStates.setting_personality)
