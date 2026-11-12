"""Qadirdon AI — Sozlamalar handleri.

Mavjud sozlamalarni ko'rish va to'liq o'zgartirish.
Barcha inline tugmalar to'liq ishlaydi.
"""

from __future__ import annotations

import os
import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from loguru import logger
from sqlalchemy import select, update

from ai.prompts.roles import ROLE_NAMES_UZ
from ai.prompts.relationship_levels import get_level_info, get_progress_bar, RELATIONSHIP_LEVELS
from ai.characters import get_character_model, list_character_models
from bot.keyboards.inline import (
    emoji_level_keyboard,
    relationship_settings_keyboard,
    settings_emotion_keyboard,
    settings_keyboard,
    settings_language_keyboard,
    settings_models_keyboard,
    settings_role_keyboard,
    settings_voice_keyboard,
    typing_speed_keyboard,
)
from bot.keyboards.reply import cancel_keyboard, main_menu_keyboard
from bot.middlewares.auth import invalidate_user_cache
from bot.states.settings import SettingsStates
from config.settings import settings
from db.models import AiProfile, User
from db.session import async_session

settings_router = Router(name="settings")

NAME_PATTERN = re.compile(r"^[a-zA-Zа-яА-ЯёЁ\u0400-\u04FFa-zA-Z\s'`'0-9\-]{2,30}$")


def _get_settings_text(profile: AiProfile, business_connected: bool, language: str = "uz") -> str:
    role_label = ROLE_NAMES_UZ.get(profile.role, profile.role)
    status = "🟢 Yoqilgan (Faol)" if profile.is_active else "🔴 O'chirilgan (Nofaol)"
    speed_map = {1: "🐢 Sekin", 2: "🚶 Normal", 3: "⚡ Tez"}
    emoji_map = {1: "😐 Kam", 2: "🙂 O'rta", 3: "😍 Ko'p"}
    lang_map = {"uz": "🇺🇿 O'zbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
    voice_map = {
        "female_soft": "👩 Ayol (Yumshoq)",
        "female_bright": "👩‍🦰 Ayol (Yorqin)",
        "female_calm": "🧕 Ayol (Vazmin)",
        "female_warm": "🌸 Ayol (Mehribon)",
        "male_warm": "👨 Erkak (Iliq)",
        "male_deep": "🧔‍♂️ Erkak (Past)",
        "male_calm": "👨‍💼 Erkak (Vazmin)",
        "male_energetic": "⚡ Erkak (Qat'iyatli)",
        "child_playful": "🧒 Bola (Quvnoq)",
    }
    voice_display = voice_map.get(profile.voice_type, profile.voice_type) if profile.voice_enabled else "O'chirilgan"
    emotion_map = {
        "auto": "🎭 Avtomatik (Xabarga mos)",
        "romantic": "❤️ Romantik / Mehrli",
        "joyful": "😂 Quvnoq / Sho'x",
        "playful": "😜 Sho'x / Nozli (Erka)",
        "comforting": "🫂 Tasalli / Dalda",
        "surprised": "😲 Hayrat / Hayajon",
        "serious": "🤔 Jiddiy / O'ychan",
        "calm": "🌸 Sokin / Vazmin",
    }
    current_em = getattr(profile, "voice_emotion", "auto") or "auto"
    emotion_display = emotion_map.get(current_em, current_em)
    b_status = "🟢 Ulangan" if business_connected else "🔴 Ulanmagan"

    level = getattr(profile, "relationship_level", 1)
    xp = getattr(profile, "trust_xp", 0)
    mode = getattr(profile, "game_mode", "story")
    level_info = get_level_info(profile.role, level)
    mode_text = "🎮 Zabt etish (Noldan)" if mode == "story" else "🌟 Klassik (To'liq yaqin)"
    progress_text = get_progress_bar(xp, level)

    return (
        "⚙️ <b>Qadirdon AI — Sozlamalar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎭 <b>Rol:</b> {role_label}\n"
        f"📝 <b>AI Ismi:</b> {profile.ai_name}\n"
        f"❤️ <b>Munosabat:</b> {level_info['title']}\n"
        f"📊 <b>Ishonch:</b> {progress_text}\n"
        f"🕹 <b>O'yin rejimi:</b> {mode_text}\n"
        f"💬 <b>Xarakter:</b> <i>{profile.personality_prompt[:70]}...</i>\n"
        f"🌐 <b>Til:</b> {lang_map.get(language, language)}\n"
        f"🔊 <b>Ovoz:</b> {voice_display}\n"
        f"🎭 <b>Ohang / Emotsiya:</b> {emotion_display}\n"
        f"😊 <b>Emoji darajasi:</b> {emoji_map.get(profile.emoji_level, str(profile.emoji_level))}\n"
        f"⌨️ <b>Yozish tezligi:</b> {speed_map.get(profile.typing_speed, str(profile.typing_speed))}\n"
        f"💡 <b>AI holati:</b> {status}\n"
        f"📱 <b>Telegram Business:</b> {b_status}\n\n"
        "Quyidagi tugmalar orqali istalgan parametrni o'zgartirishingiz mumkin:"
    )


@settings_router.message(F.text == "⚙️ Sozlamalar")
async def show_settings_menu(message: Message, user: User, state: FSMContext) -> None:
    """Sozlamalar menyusini ko'rsatadi."""
    await state.clear()
    profile = user.ai_profiles[0] if user.ai_profiles else None
    if not profile:
        async with async_session() as session:
            stmt = select(AiProfile).where(AiProfile.user_id == user.id)
            res = await session.execute(stmt)
            profile = res.scalar_one_or_none()

    if not profile:
        await message.answer("Siz hali AI profilini sozlamagansiz. /start buyrug'ini bosing.")
        return

    text = _get_settings_text(profile, bool(user.business_connection_id), user.language)
    await message.answer(text, reply_markup=settings_keyboard(), parse_mode="HTML")


@settings_router.callback_query(F.data == "settings:show")
async def settings_show_callback(call: CallbackQuery, user: User, state: FSMContext) -> None:
    """Sozlamalar asosiy ko'rinishiga qaytadi."""
    await state.clear()
    profile = user.ai_profiles[0] if user.ai_profiles else None
    if not profile:
        async with async_session() as session:
            stmt = select(AiProfile).where(AiProfile.user_id == user.id)
            res = await session.execute(stmt)
            profile = res.scalar_one_or_none()

    if profile:
        text = _get_settings_text(profile, bool(user.business_connection_id), user.language)
        await call.message.edit_text(text, reply_markup=settings_keyboard(), parse_mode="HTML")
    await call.answer()


# ── AI ni yoqish / o'chirish ────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:toggle_ai")
async def toggle_ai_status(call: CallbackQuery, user: User) -> None:
    """AI javob berishini vaqtincha to'xtatadi yoki yoqadi."""
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            profile.is_active = not profile.is_active
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].is_active = profile.is_active
            invalidate_user_cache(user.telegram_id)
            new_status = "🟢 Yoqildi" if profile.is_active else "🔴 O'chirildi"
            await call.answer(f"AI holati: {new_status}")
            text = _get_settings_text(profile, bool(user.business_connection_id), user.language)
            await call.message.edit_text(text, reply_markup=settings_keyboard(), parse_mode="HTML")


# ── Rolni o'zgartirish ──────────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:role")
async def change_role_start(call: CallbackQuery) -> None:
    """Rolni o'zgartirish uchun ro'yxatni ochadi."""
    await call.message.edit_text(
        "🎭 <b>Yangi rolni tanlang:</b>",
        reply_markup=settings_role_keyboard(),
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.callback_query(F.data.startswith("set_role:"))
async def change_role_apply(call: CallbackQuery, user: User) -> None:
    """Tanlangan rolni saqlaydi va menyuga qaytadi."""
    role_key = call.data.split(":")[1]
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            profile.role = role_key
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].role = role_key
            invalidate_user_cache(user.telegram_id)
            role_name = ROLE_NAMES_UZ.get(role_key, role_key)
            await call.answer(f"✅ Rol yangilandi: {role_name}")
            text = _get_settings_text(profile, bool(user.business_connection_id), user.language)
            await call.message.edit_text(text, reply_markup=settings_keyboard(), parse_mode="HTML")


# ── Ismni o'zgartirish ──────────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:name")
async def change_name_start(call: CallbackQuery, state: FSMContext) -> None:
    """Ismni o'zgartirishni so'raydi."""
    await state.set_state(SettingsStates.editing_name)
    await call.message.edit_text(
        "✏️ <b>AI uchun yangi ism kiriting:</b>\n"
        "<i>(2 dan 30 gacha belgi, masalan: Jasur, Mohira, Begim)</i>\n\n"
        "👇 Yangi ismni chatga yozing:",
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.message(SettingsStates.editing_name, F.text)
async def change_name_apply(message: Message, state: FSMContext, user: User) -> None:
    """Kiritilgan yangi ismni saqlaydi."""
    name = message.text.strip().title()
    if not NAME_PATTERN.match(name):
        await message.answer(
            "⚠️ <b>Noto'g'ri ism!</b>\n\n"
            "📏 Ism 2 dan 30 gacha belgi bo'lishi kerak.\n"
            "✏️ Iltimos, qaytadan yozing:",
            parse_mode="HTML",
        )
        return

    await state.clear()
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            profile.ai_name = name
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].ai_name = name
            invalidate_user_cache(user.telegram_id)
            await message.answer(f"✅ AI ismi muvaffaqiyatli <b>{name}</b> deb o'zgartirildi!", parse_mode="HTML")
            text = _get_settings_text(profile, bool(user.business_connection_id), user.language)
            await message.answer(text, reply_markup=settings_keyboard(), parse_mode="HTML")


# ── Xarakterni o'zgartirish ─────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:personality")
async def change_personality_start(call: CallbackQuery, state: FSMContext, user: User) -> None:
    """Xarakterni o'zgartirishni so'raydi."""
    await state.set_state(SettingsStates.editing_personality)
    await call.message.edit_text(
        "💬 <b>AI uchun yangi xarakter (shaxsiyat) kiriting:</b>\n\n"
        "Masalan: <i>'Har doim samimiy, hazilkash, quvnoq va do'stona munosabatda bo'l'</i>\n\n"
        "👇 Yangi xarakter tavsifini yozing:",
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.message(SettingsStates.editing_personality, F.text)
async def change_personality_apply(message: Message, state: FSMContext, user: User) -> None:
    """Kiritilgan yangi xarakterni saqlaydi."""
    text_val = message.text.strip()
    if len(text_val) < 5:
        await message.answer("⚠️ Tavsif kamida 5 ta belgidan iborat bo'lishi kerak. Qaytadan yozing:")
        return

    await state.clear()
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            profile.personality_prompt = text_val
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].personality_prompt = text_val
            invalidate_user_cache(user.telegram_id)
            await message.answer("✅ AI xarakteri muvaffaqiyatli yangilandi!")
            text = _get_settings_text(profile, bool(user.business_connection_id), user.language)
            await message.answer(text, reply_markup=settings_keyboard(), parse_mode="HTML")


# ── Tilni o'zgartirish ──────────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:language")
async def change_language_start(call: CallbackQuery) -> None:
    """Tilni tanlash menyusini ochadi."""
    await call.message.edit_text(
        "🌐 <b>Muloqot tilini tanlang:</b>",
        reply_markup=settings_language_keyboard(),
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.callback_query(F.data.startswith("set_lang:"))
async def change_language_apply(call: CallbackQuery, user: User) -> None:
    """Tilni saqlaydi va menyuga qaytadi."""
    lang_code = call.data.split(":")[1]
    async with async_session() as session:
        stmt = update(User).where(User.id == user.id).values(language=lang_code)
        await session.execute(stmt)
        await session.commit()

        # Profilni yuklash
        profile_stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        profile_res = await session.execute(profile_stmt)
        profile = profile_res.scalar_one_or_none()

    user.language = lang_code
    invalidate_user_cache(user.telegram_id)
    await call.answer("✅ Til yangilandi!")
    if profile:
        text = _get_settings_text(profile, bool(user.business_connection_id), lang_code)
        await call.message.edit_text(text, reply_markup=settings_keyboard(), parse_mode="HTML")


# ── Ovoz sozlamalari ────────────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:voice")
async def change_voice_start(call: CallbackQuery, user: User) -> None:
    """Ovoz tanlash menyusini ochadi."""
    profile = user.ai_profiles[0] if user.ai_profiles else None
    role = profile.role if profile else "qiz_dost"
    await call.message.edit_text(
        "🔊 <b>AI uchun mos ovoz turini tanlang:</b>\n"
        "<i>(Ovozli xabarlar va qo'ng'iroqlar uchun ishlatiladi)</i>",
        reply_markup=settings_voice_keyboard(role=role, show_all=False),
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.callback_query(F.data.startswith("set_vmode:"))
async def change_voice_mode(call: CallbackQuery) -> None:
    """Sozlamalarda barcha ovozlar yoki filtrlangan ovozlarni almashtirish."""
    parts = call.data.split(":")
    mode = parts[1]
    role = parts[2] if len(parts) > 2 else "qiz_dost"
    show_all = (mode == "all")
    await call.message.edit_text(
        "🔊 <b>AI uchun mos ovoz turini tanlang:</b>\n"
        "<i>(Ovozli xabarlar va qo'ng'iroqlar uchun ishlatiladi)</i>",
        reply_markup=settings_voice_keyboard(role=role, show_all=show_all),
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.callback_query(F.data.startswith("set_voice:"))
async def change_voice_apply(call: CallbackQuery, user: User) -> None:
    """Ovoz sozlamasini saqlaydi."""
    voice_key = call.data.split(":")[1]
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            if voice_key == "off":
                profile.voice_enabled = False
            else:
                profile.voice_type = voice_key
                profile.voice_enabled = True
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].voice_enabled = profile.voice_enabled
                user.ai_profiles[0].voice_type = profile.voice_type
            invalidate_user_cache(user.telegram_id)
            await call.answer("✅ Ovoz sozlamalari yangilandi!")
            text = _get_settings_text(profile, bool(user.business_connection_id), user.language)
            await call.message.edit_text(text, reply_markup=settings_keyboard(), parse_mode="HTML")


# ── Emotsiya va Ohang sozlamalari ──────────────────────────────────────────
EMOTION_SAMPLE_PHRASES: dict[str, str] = {
    "romantic": "Jonim... Sizni bugun judayam sog'indim... Kuningiz qanday o'tdi? ❤️",
    "joyful": "Haha... Voy, bugun judayam zo'r kun bo'ldi-ku! Kayfiyatim ajoyib! 😂🎉",
    "playful": "Voy qarang-a... Arazlayman hozir sizdan, tentakvoy! Nimaga kech yozdingiz? 😜😏",
    "comforting": "Eh... Xavotir olmang-a... Hammasi yaxshi bo'ladi, men doim siz bilan birgaman 🥺",
    "surprised": "Voy! Nahotki rostdan ham shunaqa bo'ldi?! Qoyil, ishonish qiyin! 😱",
    "serious": "O'ylab qoldim... Bu juda muhim masala, keling yaxshilab maslahatlashaylik 🤔",
    "calm": "Assalomu alaykum. Barchasi joyida, xotirjam suhbatlashamiz 🌸",
}

EMOTION_LABELS: dict[str, str] = {
    "auto": "🎭 Avtomatik (Xabarga mos)",
    "romantic": "❤️ Romantik / Mehrli",
    "joyful": "😂 Quvnoq / Xushchaqchaq",
    "playful": "😜 Sho'x / Nozli (Erka)",
    "comforting": "🫂 Tasalli / Dalda",
    "surprised": "😲 Hayrat / Hayajon",
    "serious": "🤔 Jiddiy / O'ychan",
    "calm": "🌸 Sokin / Vazmin",
}


@settings_router.callback_query(F.data == "settings:emotions")
async def change_emotion_start(call: CallbackQuery, user: User) -> None:
    """Emotsiya va intonatsiya ohangini tanlash menyusini ochadi."""
    profile = user.ai_profiles[0] if user.ai_profiles else None
    current_em = getattr(profile, "voice_emotion", "auto") or "auto"
    text = (
        "🎭 <b>Ovozning emotsional ohangini tanlang:</b>\n\n"
        "Har bir ohangni <b>«▶️ Tinglash»</b> tugmasi orqali bevosita eshitib ko'rishingiz mumkin.\n\n"
        "💡 <i>«Avtomatik» tanlansa, AI xabar mazmuni va emojilarga qarab o'zi eng mos ohangni tanlaydi.</i>\n\n"
        "👇 Kerakli ohangni tanlang:"
    )
    await call.message.edit_text(
        text,
        reply_markup=settings_emotion_keyboard(current_emotion=current_em),
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.callback_query(F.data.startswith("set_emotion:"))
async def change_emotion_apply(call: CallbackQuery, user: User) -> None:
    """Emotsiya ohangini saqlaydi."""
    emotion_key = call.data.split(":")[1]
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            profile.voice_emotion = emotion_key
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].voice_emotion = emotion_key
            invalidate_user_cache(user.telegram_id)
            label = EMOTION_LABELS.get(emotion_key, emotion_key)
            await call.answer(f"✅ Ohang: {label} tanlandi!")
            await call.message.edit_reply_markup(
                reply_markup=settings_emotion_keyboard(current_emotion=emotion_key),
            )


@settings_router.callback_query(F.data.startswith("preview_emotion:"))
async def on_preview_emotion(call: CallbackQuery, user: User) -> None:
    """Emotsiya namunasini ovozli xabar qilib jo'natadi."""
    emotion_key = call.data.split(":")[1]
    profile = user.ai_profiles[0] if user.ai_profiles else None
    role = profile.role if profile else "qiz_dost"
    voice_type = profile.voice_type if profile else "female_warm"

    sample_text = EMOTION_SAMPLE_PHRASES.get(
        emotion_key,
        "Assalomu alaykum! Men sizning qadirdon hamrohingizman."
    )
    label = EMOTION_LABELS.get(emotion_key, emotion_key)

    await call.answer("🎙 Emotsiya namunasi tayyorlanmoqda...")
    try:
        from voice.tts_engine import text_to_speech
        voice_file = await text_to_speech(
            sample_text,
            role=role,
            voice_type=voice_type,
            emotion=emotion_key,
        )
        if voice_file and os.path.exists(voice_file):
            try:
                await call.message.answer_voice(
                    voice=FSInputFile(voice_file),
                    caption=f"🎙 <b>{label}</b> namunasini tinglayapsiz:\n<i>«{sample_text}»</i>",
                    parse_mode="HTML",
                )
            finally:
                if os.path.exists(voice_file):
                    os.remove(voice_file)
        else:
            await call.message.answer("⚠️ Ovoz namunasini yaratishda xatolik yuz berdi.")
    except Exception as exc:
        logger.error(f"Emotsiya namunasini yuborishda xatolik: {exc}")
        await call.message.answer("⚠️ Ovoz namunasini tayyorlashda xatolik yuz berdi.")


# ── Emoji darajasi ──────────────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:emoji")
async def change_emoji_start(call: CallbackQuery) -> None:
    """Emoji darajasini tanlash."""
    await call.message.edit_text(
        "😊 <b>Emoji darajasini tanlang:</b>",
        reply_markup=emoji_level_keyboard(),
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.callback_query(F.data.startswith("emoji:"))
async def change_emoji_apply(call: CallbackQuery, user: User) -> None:
    """Emoji darajasini saqlaydi."""
    lvl = int(call.data.split(":")[1])
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            profile.emoji_level = lvl
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].emoji_level = lvl
            invalidate_user_cache(user.telegram_id)
            await call.answer("✅ Emoji darajasi yangilandi!")
            text = _get_settings_text(profile, bool(user.business_connection_id), user.language)
            await call.message.edit_text(text, reply_markup=settings_keyboard(), parse_mode="HTML")
        else:
            await call.answer()


# ── Yozish tezligi ──────────────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:speed")
async def change_speed_start(call: CallbackQuery) -> None:
    """Yozish tezligini tanlash."""
    await call.message.edit_text(
        "⌨️ <b>Yozish tezligini tanlang:</b>",
        reply_markup=typing_speed_keyboard(),
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.callback_query(F.data.startswith("speed:"))
async def change_speed_apply(call: CallbackQuery, user: User) -> None:
    """Yozish tezligini saqlaydi."""
    spd = int(call.data.split(":")[1])
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            profile.typing_speed = spd
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].typing_speed = spd
            invalidate_user_cache(user.telegram_id)
            await call.answer("✅ Yozish tezligi yangilandi!")
            text = _get_settings_text(profile, bool(user.business_connection_id), user.language)
            await call.message.edit_text(text, reply_markup=settings_keyboard(), parse_mode="HTML")
        else:
            await call.answer()


# ── Munosabat darajasi va Rejim ─────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:relationship")
async def settings_relationship_view(call: CallbackQuery, user: User) -> None:
    """Munosabat darajasi va o'yin rejimini ko'rsatadi."""
    profile = user.ai_profiles[0] if user.ai_profiles else None
    if not profile:
        async with async_session() as session:
            stmt = select(AiProfile).where(AiProfile.user_id == user.id)
            res = await session.execute(stmt)
            profile = res.scalar_one_or_none()

    if not profile:
        await call.answer("Profil topilmadi", show_alert=True)
        return

    lvl = getattr(profile, "relationship_level", 1)
    xp = getattr(profile, "trust_xp", 0)
    mode = getattr(profile, "game_mode", "story")
    progress_bar = get_progress_bar(xp, lvl)

    # Rol uchun barcha 5 darajani ko'rsatish
    role_levels = RELATIONSHIP_LEVELS.get(profile.role, RELATIONSHIP_LEVELS["qiz_dost"])
    levels_text = ""
    for l_num in range(1, 6):
        info = role_levels[l_num]
        current_marker = "👉 " if l_num == lvl and mode == "story" else "   "
        check_icon = "⭐" if l_num <= lvl else "🔒"
        levels_text += f"{current_marker}{check_icon} <b>{info['title']}</b>\n      <i>{info['desc']}</i>\n"

    mode_info = (
        "🎮 <b>Hozirgi rejim: Zabt etish</b>\n"
        "AI bilan muloqot orqali uning ko'nglini olasiz va har safar ishonch qozonganingizda darajangiz oshadi."
        if mode == "story"
        else "🌟 <b>Hozirgi rejim: Klassik</b>\n"
        "Muloqot to'g'ridan-to'g'ri maksimal 5-darajada (to'liq yaqinlik) olib boriladi."
    )

    text = (
        f"❤️ <b>Munosabat darajalari: {profile.ai_name}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 <b>Progress:</b>\n{progress_bar}\n\n"
        f"📋 <b>Barcha bosqichlar:</b>\n{levels_text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{mode_info}\n\n"
        "Kerakli rejimni tanlang:"
    )

    await call.message.edit_text(
        text,
        reply_markup=relationship_settings_keyboard(current_mode=mode),
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.callback_query(F.data.startswith("rel:mode:"))
async def settings_change_mode(call: CallbackQuery, user: User) -> None:
    """O'yin rejimini o'zgartiradi (story / classic)."""
    new_mode = call.data.split(":")[2]  # story | classic
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            profile.game_mode = new_mode
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].game_mode = new_mode
            invalidate_user_cache(user.telegram_id)
            await call.answer(f"✅ Rejim o'zgartirildi!")
            await settings_relationship_view(call, user)
        else:
            await call.answer()


@settings_router.callback_query(F.data == "rel:reset")
async def settings_reset_relationship(call: CallbackQuery, user: User) -> None:
    """Ishonch ballari va darajani 1-bosqichga nollaydi."""
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            profile.relationship_level = 1
            profile.trust_xp = 0
            profile.game_mode = "story"
            await session.commit()
            if user.ai_profiles:
                user.ai_profiles[0].relationship_level = 1
                user.ai_profiles[0].trust_xp = 0
                user.ai_profiles[0].game_mode = "story"
            invalidate_user_cache(user.telegram_id)
            await call.answer("🔄 Muloqot 1-bosqichdan qayta boshlandi!", show_alert=True)
            await settings_relationship_view(call, user)
        else:
            await call.answer()


# ── Personaj anketasi (Dossye) ─────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:dossier")
async def settings_dossier_view(call: CallbackQuery, user: User) -> None:
    """Personajning batafsil anketasi (yoshi, kasbi, hayoti, kun tartibi)."""
    profile = user.ai_profiles[0] if user.ai_profiles else None
    if not profile:
        async with async_session() as session:
            stmt = select(AiProfile).where(AiProfile.user_id == user.id)
            res = await session.execute(stmt)
            profile = res.scalar_one_or_none()

    if not profile:
        await call.answer("Profil topilmadi", show_alert=True)
        return

    char_id = getattr(profile, "character_id", None)
    model = get_character_model(profile.role, char_id) if char_id else None

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    if model:
        text = (
            f"📋 <b>Personaj Dossiyesi: {model['badge']} {model['name']} ({model['age']} yosh)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📍 <b>Yashash joyi:</b> {model['location']}\n"
            f"💼 <b>Kasbi / O'qishi:</b> {model['profession']}\n\n"
            f"📝 <b>Hayoti va Tarixi:</b>\n<i>{model['bio']}</i>\n\n"
            f"⏰ <b>Kun tartibi:</b>\n<i>{model['schedule']}</i>\n\n"
            f"🗣 <b>O'ziga xos iboralari:</b>\n<i>{', '.join(model.get('slangs', []))}</i>\n"
        )
    else:
        text = (
            f"📋 <b>Personaj ma'lumotlari: {profile.ai_name}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🎭 <b>Rol:</b> {profile.role}\n"
            f"💬 <b>Xarakter:</b> <i>{profile.personality_prompt}</i>\n\n"
            "💡 <i>Siz tayyor hayotiy personaj modelini tanlashingiz mumkin!</i>\n"
        )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎭 Modelni almashtirish", callback_data="settings:choose_model")],
            [InlineKeyboardButton(text="🔙 Sozlamalarga qaytish", callback_data="settings:show")],
        ]
    )
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await call.answer()


@settings_router.callback_query(F.data == "settings:choose_model")
async def settings_choose_model_menu(call: CallbackQuery, user: User) -> None:
    """Mavjud modellardan birini tanlash menyusi."""
    profile = user.ai_profiles[0] if user.ai_profiles else None
    role = profile.role if profile else "qiz_dost"
    models = list_character_models(role)

    if not models:
        await call.answer("Bu rol uchun hozircha tayyor modellar mavjud emas", show_alert=True)
        return

    text = (
        "🌟 <b>Quyidagi haqiqiy hayotiy modellardan birini tanlang:</b>\n\n"
        "<i>Har bir personajning o'z ismi, yoshi, dardi, kun tartibi va o'ziga xos sirlari bor!</i>"
    )
    await call.message.edit_text(
        text,
        reply_markup=settings_models_keyboard(role),
        parse_mode="HTML",
    )
    await call.answer()


@settings_router.callback_query(F.data.startswith("set_model:"))
async def settings_apply_model(call: CallbackQuery, user: User) -> None:
    """Tanlangan modelni profilga saqlaydi."""
    model_id = call.data.split(":")[1]
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()
        if profile:
            model = get_character_model(profile.role, model_id)
            if model:
                profile.character_id = model["id"]
                profile.ai_name = model["name"]
                profile.personality_prompt = model["bio"]
                await session.commit()
                if user.ai_profiles:
                    user.ai_profiles[0].character_id = model["id"]
                    user.ai_profiles[0].ai_name = model["name"]
                    user.ai_profiles[0].personality_prompt = model["bio"]
                invalidate_user_cache(user.telegram_id)
                await call.answer(f"✅ {model['name']} personaji faollashtirildi!", show_alert=True)
                await settings_dossier_view(call, user)
                return
    await call.answer()


# ── Kvestlar va Sirlar ──────────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:quests")
async def settings_quests_view(call: CallbackQuery, user: User) -> None:
    """Personajning barcha kvestlari (Oddiy, Favqulodda, Yashirin) ni ko'rsatadi."""
    profile = user.ai_profiles[0] if user.ai_profiles else None
    if not profile:
        async with async_session() as session:
            stmt = select(AiProfile).where(AiProfile.user_id == user.id)
            res = await session.execute(stmt)
            profile = res.scalar_one_or_none()

    if not profile:
        await call.answer("Profil topilmadi", show_alert=True)
        return

    char_id = getattr(profile, "character_id", None)
    model = get_character_model(profile.role, char_id) if char_id else None
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    if not model or "quests" not in model:
        text = (
            "🎯 <b>Kvestlar tizimi</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Bu personaj uchun maxsus kvestlar mavjud emas.\n"
            "Tayyor hayotiy personajni tanlab, qiziqarli kvestlar va sirlarni ochishingiz mumkin!"
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎭 Personaj tanlash", callback_data="settings:choose_model")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings:show")],
            ]
        )
        await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await call.answer()
        return

    quests = model.get("quests", {})
    normal_q = quests.get("normal", {})
    urgent_q = quests.get("urgent", {})
    secret = model.get("secret_trigger", {})

    unlocked = profile.unlocked_secrets or []
    secret_id = f"{model.get('id')}_secret"
    is_secret_unlocked = secret_id in unlocked

    secret_status = (
        f"⭐ <b>{secret.get('title')}</b> (OCHILGAN!)\n<i>{secret.get('story')}</i>"
        if is_secret_unlocked
        else "🔒 <b>Yashirin kvest:</b> <i>Muloqot davomida personajning maxsus xotirasi yoki sirini oching! (+80-100 EXP)</i>"
    )

    text = (
        f"🎯 <b>{model['name']} — Kvestlar va Sirlar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🟢 <b>Oddiy kvest: {normal_q.get('title', '')}</b>\n"
        f"📝 <i>{normal_q.get('desc', '')}</i>\n"
        f"🎁 Mukofot: <b>+{normal_q.get('reward_xp', 20)} EXP</b>\n\n"
        f"🚨 <b>Favqulodda kvest: {urgent_q.get('title', '')}</b>\n"
        f"📝 <i>{urgent_q.get('desc', '')}</i>\n"
        f"🎁 Mukofot: <b>+{urgent_q.get('reward_xp', 50)} EXP</b> | Jarima: <b>-{urgent_q.get('penalty_xp', 25)} EXP</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🗝️ <b>Yashirin sir / Kvest:</b>\n{secret_status}\n\n"
        "💡 <i>Kvestlar chatda tabiiy suhbatlashish orqali avtomatik bajariladi!</i>"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Sozlamalarga qaytish", callback_data="settings:show")],
        ]
    )
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await call.answer()


# ── Orqaga ──────────────────────────────────────────────────────────────────
@settings_router.callback_query(F.data == "settings:back")
async def settings_back(call: CallbackQuery, user: User, state: FSMContext) -> None:
    """Sozlamalarni yopadi."""
    await state.clear()
    is_adm = user.telegram_id in settings.admin_id_list
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(
        "Boshqaruv menyusi:",
        reply_markup=main_menu_keyboard(is_admin=is_adm),
    )
    await call.answer()
