"""Qadirdon AI — Ovoz sozlamalari va Sozlashni Tasdiqlash handleri.

Ovoz turini tanlash va AI profilini bazaga saqlash.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from sqlalchemy import select

from bot.keyboards.inline import confirm_keyboard
from bot.keyboards.reply import main_menu_keyboard
from bot.middlewares.auth import invalidate_user_cache
from bot.states.setup import SetupStates
from config.settings import settings
from db.models import AiProfile, Subscription, User
from db.session import async_session

setup_voice_router = Router(name="setup_voice")

# ── Rol guruhlari ────────────────────────────────────────────────────────────
FEMALE_ROLES = {"qiz_dost", "ayol", "ona", "opa", "singil"}
MALE_ROLES = {"aka", "uka"}

# ── Barcha ovoz turlari ──────────────────────────────────────────────────────
VOICE_TYPES = {
    # Ayollar / Qizlar ovozlari
    "female_soft": "👩 Ayol — Yumshoq va mayin",
    "female_bright": "👩‍🦰 Ayol — Yorqin va sho'x",
    "female_calm": "🧕 Ayol — Vazmin va samimiy",
    "female_warm": "🌸 Ayol — Mehribon va iliq",
    # Erkaklar ovozlari
    "male_warm": "👨 Erkak — Samimiy va iliq",
    "male_deep": "🧔‍♂️ Erkak — Salobatli va past",
    "male_calm": "👨‍💼 Erkak — Vazmin va bosiq",
    "male_energetic": "⚡ Erkak — Qat'iyatli yigit",
    # Bolalar / Kenjatoylar uchun
    "child_playful": "🧒 Bola / Kenjatoy — Quvnoq",
}

FEMALE_VOICE_KEYS = ["female_soft", "female_bright", "female_calm", "female_warm"]
MALE_VOICE_KEYS = ["male_warm", "male_deep", "male_calm", "male_energetic"]


def voice_type_keyboard(role: str = "qiz_dost", show_all: bool = False) -> InlineKeyboardMarkup:
    """Rolga mos ovoz turi tanlash klaviaturasi."""
    buttons = []

    if show_all:
        for key, label in VOICE_TYPES.items():
            buttons.append([InlineKeyboardButton(text=label, callback_data=f"voice:{key}")])
        buttons.append([InlineKeyboardButton(text="🔙 Mos ovozlarga qaytish", callback_data=f"vmode:filter:{role}")])
    else:
        if role in FEMALE_ROLES:
            keys = list(FEMALE_VOICE_KEYS)
            if role == "singil":
                keys.append("child_playful")
        elif role in MALE_ROLES:
            keys = list(MALE_VOICE_KEYS)
            if role == "uka":
                keys.append("child_playful")
        else:
            keys = list(VOICE_TYPES.keys())

        for key in keys:
            label = VOICE_TYPES.get(key, key)
            buttons.append([InlineKeyboardButton(text=label, callback_data=f"voice:{key}")])

        buttons.append([InlineKeyboardButton(text="🌐 Barcha ovozlarni ko'rish", callback_data=f"vmode:all:{role}")])

    buttons.append([InlineKeyboardButton(text="⏩ O'tkazib yuborish", callback_data="voice:skip")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@setup_voice_router.callback_query(
    SetupStates.setting_typing_speed,
    F.data.startswith("speed:"),
)
async def on_typing_speed_chosen(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    """Yozish tezligi tanlangandan keyin ovoz sozlamalariga o'tadi."""
    await callback.answer()

    speed = int(callback.data.split(":")[1])
    speed_names = {1: "🐢 Sekin", 2: "🚶 Normal", 3: "⚡ Tez"}
    speed_name = speed_names.get(speed, "Normal")

    await state.update_data(typing_speed=speed)

    data = await state.get_data()
    ai_name = data.get("ai_name", "Qadirdon").strip().title()
    role = data.get("role", "qiz_dost")

    text = (
        f"✅ Yozish tezligi: <b>{speed_name}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔊 <b>4-qadam: {ai_name} uchun mos ovozni tanlang:</b>\n\n"
        "🎙️ Bu sozlama kelajakda ovozli qo'ng'iroqlar\n"
        "va ovozli xabarlar uchun ishlatiladi.\n\n"
        "👇 Ovoz turini tanlang yoki o'tkazib yuboring:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=voice_type_keyboard(role=role, show_all=False),
        parse_mode="HTML",
    )


@setup_voice_router.callback_query(F.data.startswith("vmode:"))
async def on_voice_mode_toggle(callback: CallbackQuery, state: FSMContext) -> None:
    """Barcha ovozlar va filtrlangan ovozlar o'rtasida almashtirish."""
    await callback.answer()
    parts = callback.data.split(":")
    mode = parts[1]  # all | filter
    role = parts[2] if len(parts) > 2 else "qiz_dost"
    show_all = (mode == "all")

    data = await state.get_data()
    ai_name = data.get("ai_name", "Qadirdon").strip().title()
    speed = data.get("typing_speed", 2)
    speed_names = {1: "🐢 Sekin", 2: "🚶 Normal", 3: "⚡ Tez"}
    speed_name = speed_names.get(speed, "Normal")

    text = (
        f"✅ Yozish tezligi: <b>{speed_name}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔊 <b>4-qadam: {ai_name} uchun mos ovozni tanlang:</b>\n\n"
        "🎙️ Bu sozlama kelajakda ovozli qo'ng'iroqlar\n"
        "va ovozli xabarlar uchun ishlatiladi.\n\n"
        "👇 Ovoz turini tanlang yoki o'tkazib yuboring:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=voice_type_keyboard(role=role, show_all=show_all),
        parse_mode="HTML",
    )


@setup_voice_router.callback_query(
    F.data.startswith("voice:"),
)
async def on_voice_chosen(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    """Ovoz turi tanlash callback'ini qayta ishlaydi va xulosani ko'rsatadi."""
    await callback.answer()

    voice_key = callback.data.split(":")[1]
    data = await state.get_data()
    role = data.get("role", "qiz_dost")

    if voice_key == "skip":
        default_voice = "female_soft" if role in FEMALE_ROLES else "male_warm"
        await state.update_data(voice_type=default_voice, voice_enabled=False)
    else:
        await state.update_data(voice_type=voice_key, voice_enabled=True)

    data = await state.get_data()
    ai_name = data.get("ai_name", "Qadirdon").strip().title()
    personality = data.get("personality_prompt", "")
    emoji_lvl = data.get("emoji_level", 2)
    speed = data.get("typing_speed", 2)
    v_type = data.get("voice_type", "female_soft" if role in FEMALE_ROLES else "male_warm")
    v_enabled = data.get("voice_enabled", False)
    lang = data.get("language", "uz")

    role_names = {
        "aka": "👨 Aka", "uka": "👦 Uka", "opa": "👩 Opa",
        "singil": "👧 Singil", "ona": "🤱 Ona",
        "qiz_dost": "💕 Qiz do'st", "ayol": "💍 Ayol",
    }
    emoji_names = {1: "😐 Kam", 2: "🙂 O'rta", 3: "😍 Ko'p"}
    speed_names = {1: "🐢 Sekin", 2: "🚶 Normal", 3: "⚡ Tez"}
    lang_names = {"uz": "🇺🇿 O'zbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
    voice_display = VOICE_TYPES.get(v_type, v_type) if v_enabled else "⏩ O'tkazib yuborildi"

    mode = data.get("game_mode", "story")
    mode_text = "🎮 Zabt etish (Story, 1-darajadan)" if mode == "story" else "🌟 Klassik (Maksimal yaqinlik, 5-daraja)"

    summary = (
        "📋 <b>5-qadam: Yakuniy sozlamalar xulosasi:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 <b>Til:</b> {lang_names.get(lang, lang)}\n"
        f"🎭 <b>Rol:</b> {role_names.get(role, role)}\n"
        f"👤 <b>Personaj:</b> {ai_name}\n"
        f"🕹 <b>Rejim:</b> {mode_text}\n"
        f"📝 <b>Hayoti:</b> <i>{personality[:80]}{'...' if len(personality) > 80 else ''}</i>\n"
        f"😊 <b>Emoji:</b> {emoji_names.get(emoji_lvl, str(emoji_lvl))}\n"
        f"⌨️ <b>Tezlik:</b> {speed_names.get(speed, str(speed))}\n"
        f"🔊 <b>Ovoz:</b> {voice_display}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ <b>Barchasi to'g'rimi? Tasdiqlaysizmi?</b>"
    )
    await callback.message.edit_text(
        summary,
        reply_markup=confirm_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(SetupStates.confirming)


# ── Tasdiqlash (confirm:yes) ────────────────────────────────────────────────
@setup_voice_router.callback_query(
    SetupStates.confirming,
    F.data == "confirm:yes",
)
async def on_setup_confirmed(
    callback: CallbackQuery, state: FSMContext, user: User
) -> None:
    """Barcha sozlamalarni bazaga saqlaydi va asosiy menyuga o'tkazadi."""
    await callback.answer()
    data = await state.get_data()
    await state.clear()

    async with async_session() as session:
        # User profilini tekshirish
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        result = await session.execute(stmt)
        profile = result.scalar_one_or_none()

        if profile is None:
            profile = AiProfile(user_id=user.id)
            session.add(profile)

        role = data.get("role", "aka")
        default_v = "female_soft" if role in FEMALE_ROLES else "male_warm"

        mode = data.get("game_mode", "story")
        profile.role = role
        profile.ai_name = data.get("ai_name", "Qadirdon").strip().title()
        profile.character_id = data.get("character_id")
        profile.game_mode = mode
        profile.relationship_level = 1 if mode == "story" else 5
        profile.trust_xp = 0 if mode == "story" else 1000
        profile.unlocked_secrets = []
        profile.message_splitting = True
        profile.personality_prompt = data.get(
            "personality_prompt", "Samimiy, mehribon va g'amxo'r."
        )
        profile.emoji_level = data.get("emoji_level", 2)
        profile.typing_speed = data.get("typing_speed", 2)
        profile.voice_type = data.get("voice_type", default_v)
        profile.voice_enabled = data.get("voice_enabled", False)
        profile.is_active = True

        # Obuna yo'q bo'lsa bepul obuna yaratish
        sub_stmt = select(Subscription).where(Subscription.user_id == user.id)
        sub_res = await session.execute(sub_stmt)
        sub = sub_res.scalar_one_or_none()
        if sub is None:
            sub = Subscription(user_id=user.id, plan="free")
            session.add(sub)

        await session.commit()

        # Cache ni tozalash
        invalidate_user_cache(user.telegram_id)

    logger.info("Foydalanuvchi {} AI profilini to'liq sozladi: {}", user.telegram_id, profile.ai_name)

    is_adm = callback.from_user.id in settings.admin_id_list if callback.from_user else False

    congrats_text = (
        f"🎉 <b>Tabriklaymiz! {profile.ai_name} to'liq sozlandi va faollashtirildi!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📱 <b>Endi nima qilish kerak?</b>\n"
        "1. Telegram sozlamalariga kiring.\n"
        "2. <b>Telegram Business -> Chatbotlar</b> bo'limini oching.\n"
        "3. Ushbu botimizning username'ini qidiring va ulanishga ruxsat bering.\n\n"
        "🚀 Shundan so'ng, istalgan odam sizning shaxsiy profilingizga yozsa, "
        f"<b>{profile.ai_name}</b> sizning nomingizdan insondek muloqot qiladi!\n\n"
        "👇 Asosiy boshqaruv menyusi:"
    )
    await callback.message.edit_text(congrats_text, parse_mode="HTML")
    await callback.message.answer(
        "Quyidagi menyu orqali sozlamalarni boshqarishingiz mumkin:",
        reply_markup=main_menu_keyboard(is_admin=is_adm),
    )


# ── Bekor qilish (confirm:no) ───────────────────────────────────────────────
@setup_voice_router.callback_query(
    SetupStates.confirming,
    F.data == "confirm:no",
)
async def on_setup_cancelled(
    callback: CallbackQuery, state: FSMContext, user: User
) -> None:
    """Sozlashni bekor qiladi."""
    await callback.answer()
    await state.clear()
    is_adm = callback.from_user.id in settings.admin_id_list if callback.from_user else False
    await callback.message.edit_text(
        "❌ <b>Sozlash bekor qilindi.</b>\n"
        "Istalgan vaqtda qaytadan sozlash uchun /start buyrug'ini bosing.",
        parse_mode="HTML",
    )
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=main_menu_keyboard(is_admin=is_adm),
    )
