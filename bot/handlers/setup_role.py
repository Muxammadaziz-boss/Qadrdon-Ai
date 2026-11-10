"""Qadirdon AI — Rol va Personaj tanlash handleri.

Foydalanuvchi mavjud real personaj modellaridan birini tanlaydi
va to'g'ridan-to'g'ri uning xarakteri va ma'lumotlari o'rnatiladi.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.inline import (
    character_model_keyboard,
    emoji_level_keyboard,
    game_mode_keyboard,
    role_keyboard,
)
from ai.characters import list_character_models, get_character_model
from bot.states.setup import SetupStates
from db.models import User

setup_role_router = Router(name="setup_role")

# ── Rol ma'lumotlari ────────────────────────────────────────────────────────
ROLE_INFO = {
    "aka": ("👨 Aka", "Katta aka — himoyachi, maslahatchi va ishonchli suyanchiq"),
    "uka": ("👦 Uka", "Kichik uka — samimiy, quvnoq va sadoqatli"),
    "opa": ("👩 Opa", "Katta opa — g'amxo'r, mehribon va doimo yoningizda"),
    "singil": ("👧 Singil", "Kichik singil — erka, yoqimtoy va beg'ubor qalbli"),
    "ona": ("🤱 Ona", "Mehribon ona — har doim tushunadi, duo qiladi va suyanchiq bo'ladi"),
    "qiz_dost": ("💕 Qiz do'st", "Qiz do'st — samimiy, romantik va nozik qalbli hamroh"),
    "ayol": ("💍 Ayol / Turmush o'rtog'i", "Vafoli rafiqa — oila bekasi, mehr-muhabbat va sadoqat timsoli"),
}


@setup_role_router.callback_query(
    SetupStates.choosing_role,
    F.data.startswith("role:"),
)
async def on_role_chosen(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    """Rol tanlash callback'ini qayta ishlaydi va mavjud personajlar ro'yxatini ko'rsatadi."""
    await callback.answer()

    role_key = callback.data.split(":")[1]
    role_name, role_desc = ROLE_INFO.get(role_key, (role_key, ""))

    await state.update_data(role=role_key)

    text = (
        f"🎭 <b>Rol tanlandi: {role_name}</b>\n"
        f"📝 <i>{role_desc}</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌟 <b>Mavjud hayotiy personajlardan birini tanlang:</b>\n"
        "<i>Har bir personajning o'z ismi, yoshi, kasbi, hayotiy dardi va o'ziga xos sirlari bor!</i>\n\n"
        "👇 O'zingizga yoqqan qahramonni tanlang:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=character_model_keyboard(role_key),
        parse_mode="HTML",
    )
    await state.set_state(SetupStates.choosing_character_model)


@setup_role_router.callback_query(F.data == "back_to_roles")
async def on_back_to_roles(callback: CallbackQuery, state: FSMContext) -> None:
    """Rollar tanlash menyusiga qaytish."""
    await callback.answer()
    welcome_text = (
        "🎭 <b>Personaj rolini tanlang:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Har bir rolda o'zining ismi, yoshi, kasbi va sirlariga ega tayyor qahramonlar mavjud.\n\n"
        "👇 Qaysi roldagi personajni tanlamoqchisiz?"
    )
    await callback.message.edit_text(
        welcome_text,
        reply_markup=role_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(SetupStates.choosing_role)


@setup_role_router.callback_query(
    SetupStates.choosing_character_model,
    F.data.startswith("charmodel:"),
)
async def on_character_model_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """Mavjud personaj modeli tanlanganda uning to'liq ma'lumotini yuklaydi va emoji sozlashga o'tadi."""
    await callback.answer()
    choice = callback.data.split(":")[1]
    data = await state.get_data()
    role_key = data.get("role", "qiz_dost")

    # Model ma'lumotlarini olish
    model = get_character_model(role_key, choice)
    if not model:
        await callback.answer("Personaj topilmadi", show_alert=True)
        return

    await state.update_data(
        ai_name=model["name"],
        character_id=model["id"],
        personality_prompt=model["bio"],
    )

    text = (
        f"✅ <b>Tanlangan personaj: {model['badge']} {model['name']} ({model['age']} yosh)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 <b>Yashash joyi:</b> {model['location']}\n"
        f"💼 <b>Kasbi:</b> {model['profession']}\n"
        f"📝 <b>Hayoti:</b> <i>{model['bio']}</i>\n"
        f"⏰ <b>Kun tartibi:</b> <i>{model['schedule']}</i>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🕹 <b>1-qadam: {model['name']} bilan muloqot rejimini tanlang:</b>\n\n"
        "🎮 <b>Zabt etish (Story rejim):</b>\n"
        "• Munosabat 1-bosqichdan (\"Siz\", rasmiy) boshlanadi;\n"
        "• Suhbatlar orqali uning ishonchini qozonasiz va ko'nglini olasiz;\n"
        "• Har safar yangi daraja, yashirin sirlar va kvestlar ochiladi.\n\n"
        "🌟 <b>Klassik rejim:</b>\n"
        "• Boshidanoq to'liq yaqinlik (5-daraja) va cheksiz mehr;\n"
        "• Sinovlarsiz erkin, sirdoshona va erkalashlar bilan muloqot.\n\n"
        "👇 Qaysi rejim sizga ma'qul?"
    )
    await callback.message.edit_text(text, reply_markup=game_mode_keyboard(), parse_mode="HTML")
    await state.set_state(SetupStates.choosing_game_mode)


@setup_role_router.callback_query(
    SetupStates.choosing_game_mode,
    F.data.startswith("setup_mode:"),
)
async def on_game_mode_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    """O'yin rejimi tanlanganda saqlaydi va emoji darajasini belgilashga o'tadi."""
    await callback.answer()
    mode = callback.data.split(":")[1]  # story | classic
    await state.update_data(game_mode=mode)

    data = await state.get_data()
    ai_name = data.get("ai_name", "Qadirdon")
    mode_title = "🎮 Zabt etish (Story)" if mode == "story" else "🌟 Klassik"

    text = (
        f"✅ Rejim tanlandi: <b>{mode_title}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"😊 <b>2-qadam: {ai_name} qanchalik darajada emoji ishlatsin?</b>\n\n"
        "😐 <b>Kam</b> — Deyarli emoji ishlatmaydi\n"
        "🙂 <b>O'rta</b> — Ba'zan emoji qo'shadi\n"
        "😍 <b>Ko'p</b> — Har xabarda emojilar bilan to'liq\n\n"
        "👇 Emoji darajasini tanlang:"
    )
    await callback.message.edit_text(text, reply_markup=emoji_level_keyboard(), parse_mode="HTML")
    await state.set_state(SetupStates.setting_emoji_level)
