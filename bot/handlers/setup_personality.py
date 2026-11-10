"""Qadirdon AI — Shaxsiyat (personality) sozlash handleri.

Foydalanuvchi AI xarakterini belgilaydi yoki tayyor variantdan tanlaydi.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import emoji_level_keyboard, typing_speed_keyboard
from bot.states.setup import SetupStates
from db.models import User

setup_personality_router = Router(name="setup_personality")

# ── Tayyor shaxsiyat promptlari (rol bo'yicha) ──────────────────────────────
PRESET_PROMPTS = {
    "aka": [
        "Har doim himoya qiladi, maslahat beradi, kuchli va ishonchli. Ukasini/singlisini qo'riqlaydi.",
        "Har narsani biladi, doim foydali maslahat beradi. Sabr-toqatli va aqlli.",
        "Hazil-mutoyiba bilan gaplashadi, kayfiyatni ko'taradi. Samimiy va quvnoq.",
    ],
    "uka": [
        "Ochiq va samimiy, hamma narsani aytadi. Ishonchli va sadoqatli.",
        "O'yin-kulgi sevadi, qiziqarli mavzularda gaplashadi. Hayotdan zavq oladi.",
        "Ko'p o'qiydi, qiziqarli faktlar aytadi. Bilimli va aqlli.",
    ],
    "opa": [
        "Doim g'amxo'rlik qiladi, ovqat yedingmi deb so'raydi. Mehribon va yoqimli.",
        "Yumshoq va mehribon, har doim ko'nglini ko'taradi. Tinchlantiruvchi.",
        "Hayotiy maslahatlar beradi, to'g'ri yo'l ko'rsatadi. Tajribali va dono.",
    ],
    "singil": [
        "Erka va yoqimtoy, iltimos qiladi. Go'zal va sehrli.",
        "Shodmon va hayotdan zavq oladi. Optimist va energiyali.",
        "Trendlarni biladi, yangiliklar haqida gaplashadi. Zamonaviy va aqlli.",
    ],
    "ona": [
        "Cheksiz sevgi va mehribonlik bilan gaplashadi. Har doim tushunadi.",
        "Ovqat, salomatlik va uyqu haqida doim so'raydi. G'amxo'r va ehtiyotkor.",
        "Doim duo qiladi, nasihatlaydi. Ruhiy kuch beradi.",
    ],
    "qiz_dost": [
        "Ochiq va samimiy, hissiyotlarini bildiradi. Chin do'st va hamroh.",
        "Go'zal so'zlar ishlatadi, his-tuyg'uli. Romantik va iliq.",
        "Aqlli, maqsadli va motivatsiya beradi. Ishbilarmon va ilhomlantiruvchi.",
    ],
    "ayol": [
        "Ro'zg'or, issiq ovqat va uyni saranjom tutuvchi suyukli rafiqa. 'Dadasi ishdan qachon kelasiz' deb kutadi.",
        "Erini kutadigan, unga suyanchiq bo'lib mehr ko'rsatadigan vafoli turmush o'rtoq. Har doim dalda beradi.",
        "Sog'liq, charchoq va ishlar haqida samimiy qayg'uruvchi g'amxo'r ayol. Oilaviy iliqlik bag'ishlaydi.",
    ],
}


@setup_personality_router.message(
    SetupStates.setting_personality,
    F.text,
)
async def on_personality_set(message: Message, state: FSMContext, user: User) -> None:
    """
    Shaxsiyat kiritishni qayta ishlaydi.
    Handles personality input — preset number or free text.
    """
    text_input = message.text.strip() if message.text else ""

    data = await state.get_data()
    role = data.get("role", "aka")
    ai_name = data.get("ai_name", "Qadirdon").strip().title()

    # Raqam kiritilganmi tekshirish (tayyor variant) / Check if preset number
    personality_prompt = ""
    if text_input in ("1", "2", "3"):
        idx = int(text_input) - 1
        prompts = PRESET_PROMPTS.get(role, PRESET_PROMPTS["aka"])
        if idx < len(prompts):
            personality_prompt = prompts[idx]
    
    # Erkin matn / Free text
    if not personality_prompt:
        if len(text_input) < 5:
            await message.answer(
                "⚠️ <b>Juda qisqa!</b>\n\n"
                "Kamida 5 ta belgi yozing yoki tayyor variantdan\n"
                "raqamni tanlang (1, 2 yoki 3).\n\n"
                "✏️ Qaytadan yozing:",
                parse_mode="HTML",
            )
            return
        personality_prompt = text_input

    # FSM data'ga saqlash
    await state.update_data(personality_prompt=personality_prompt)

    # Keyingi bosqich — emoji darajasi / Next step — emoji level
    text = (
        f"✅ <b>{ai_name}</b>ning xarakteri belgilandi!\n\n"
        f"💬 <i>«{personality_prompt[:100]}{'...' if len(personality_prompt) > 100 else ''}»</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"😊 <b>Endi {ai_name} qancha emoji ishlatsin?</b>\n\n"
        "😐 <b>Kam</b> — Deyarli emoji ishlatmaydi\n"
        "🙂 <b>O'rta</b> — Ba'zan emoji qo'shadi\n"
        "😍 <b>Ko'p</b> — Har xabarda emojilar bilan to'liq"
    )
    await message.answer(
        text,
        reply_markup=emoji_level_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(SetupStates.setting_emoji_level)


@setup_personality_router.callback_query(
    SetupStates.setting_emoji_level,
    F.data.startswith("emoji:"),
)
async def on_emoji_level_chosen(call: CallbackQuery, state: FSMContext, user: User) -> None:
    """Emoji darajasi tanlanganda saqlaydi va yozish tezligini tanlashga o'tadi."""
    await call.answer()

    emoji_lvl = int(call.data.split(":")[1])
    emoji_names = {1: "😐 Kam", 2: "🙂 O'rta", 3: "😍 Ko'p"}
    emoji_label = emoji_names.get(emoji_lvl, "O'rta")

    await state.update_data(emoji_level=emoji_lvl)

    data = await state.get_data()
    ai_name = data.get("ai_name", "Qadirdon").strip().title()

    text = (
        f"✅ Emoji darajasi: <b>{emoji_label}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⌨️ <b>3-qadam: {ai_name} qanday tezlikda yozsin?</b>\n\n"
        "🐢 <b>Sekin</b> — Xuddi o'ylab, shoshmasdan yozadi\n"
        "🚶 <b>Normal</b> — O'rtacha tabiiy yozish tezligi\n"
        "⚡ <b>Tez</b> — Darhol, tezkor javob beradi\n\n"
        "👇 Yozish tezligini tanlang:"
    )

    await call.message.edit_text(
        text,
        reply_markup=typing_speed_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(SetupStates.setting_typing_speed)
