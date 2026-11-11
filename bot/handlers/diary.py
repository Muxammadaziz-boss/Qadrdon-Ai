"""Qadirdon AI — Munosabatlar Kundaligi va Dossye (Relationship Diary).

Foydalanuvchi va AI hamrohi o'rtasidagi muloqot tarixi, ishonch darajasi,
ochilgan shaxsiy sirlar va eslab qolingan uzoq muddatli faktlar kundaligi.
"""

from __future__ import annotations

from datetime import datetime, timezone
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from sqlalchemy import func, select

from ai.characters import get_character_model, list_character_models
from ai.prompts.relationship_levels import (
    RELATIONSHIP_LEVELS,
    LEVEL_THRESHOLDS,
    get_progress_bar,
)
from config.settings import settings
from db.models import AiProfile, Conversation, Message, User, UserFact
from db.session import async_session

diary_router = Router(name="diary_router")


def diary_keyboard() -> InlineKeyboardMarkup:
    """Kundalik asosiy klaviaturasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔐 Ochilgan sirlar", callback_data="diary:secrets"),
                InlineKeyboardButton(text="🧠 Eslab qolingan faktlar", callback_data="diary:facts"),
            ],
            [
                InlineKeyboardButton(text="🎮 Rejim va Darajalar", callback_data="settings:relationship"),
                InlineKeyboardButton(text="🔄 Yangilash", callback_data="diary:show"),
            ],
            [
                InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings:show"),
            ],
        ]
    )


def back_to_diary_keyboard() -> InlineKeyboardMarkup:
    """Kundalikka qaytish tugmasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Kundalikka qaytish", callback_data="diary:show")],
        ]
    )


@diary_router.message(F.text == "📖 Kundalik")
@diary_router.message(Command("diary"))
@diary_router.message(Command("kundalik"))
async def show_diary_message(message: types.Message, user: User) -> None:
    """Kundalikni ko'rsatish (xabar orqali)."""
    text, kb = await render_diary_content(user)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@diary_router.callback_query(F.data == "diary:show")
async def show_diary_callback(call: CallbackQuery, user: User) -> None:
    """Kundalikni ko'rsatish / yangilash (callback orqali)."""
    text, kb = await render_diary_content(user)
    try:
        await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await call.answer("🔄 Kundalik yangilandi!")


async def render_diary_content(user: User) -> tuple[str, InlineKeyboardMarkup]:
    """Kundalik kartasi matnini yaratadi."""
    async with async_session() as session:
        # Profilni olish
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()

        if not profile:
            return (
                "⚠️ <b>Profil topilmadi.</b>\nIltimos, avval /start orqali AI profilingizni sozlang.",
                diary_keyboard(),
            )

        # Suhbat xabarlar statistikasini olish
        conv_stmt = select(func.coalesce(func.sum(Conversation.message_count), 0)).where(
            Conversation.user_id == user.id
        )
        conv_res = await session.execute(conv_stmt)
        total_messages = conv_res.scalar_one()

        # Saqlangan faktlar soni
        fact_count_stmt = select(func.count(UserFact.id)).where(UserFact.user_id == user.id)
        fact_count_res = await session.execute(fact_count_stmt)
        total_facts = fact_count_res.scalar_one()

    # Birga o'tgan kunlar
    now = datetime.now(timezone.utc)
    created_at = profile.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    days_together = max(1, (now - created_at).days + 1)

    lvl = profile.relationship_level or 1
    xp = profile.trust_xp or 0
    mode = profile.game_mode or "story"
    mode_badge = "🎮 Zabt etish (Story)" if mode == "story" else "🌟 Klassik (Erkin)"

    role_levels = RELATIONSHIP_LEVELS.get(profile.role, RELATIONSHIP_LEVELS["qiz_dost"])
    current_level_info = role_levels.get(lvl, role_levels[1])
    progress_bar = get_progress_bar(xp, lvl)

    # Keyingi darajagacha qolgan ball
    next_threshold = LEVEL_THRESHOLDS.get(min(5, lvl + 1), 1000)
    remaining_xp = max(0, next_threshold - xp)

    # Ochilgan sirlar
    unlocked = profile.unlocked_secrets or []
    secrets_count = len(unlocked)

    role_names = {
        "qiz_dost": "💖 Qiz do'st",
        "ayol": "💍 Ayol",
        "ona": "🤱 Ona",
        "aka": "👨 Aka",
        "uka": "👦 Uka",
        "opa": "👩 Opa",
        "singil": "👧 Singil",
    }
    role_title = role_names.get(profile.role, profile.role)

    text = (
        f"📖 <b>Munosabatlar Kundaligi & Dossye</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Hamrohingiz:</b> {profile.ai_name} ({role_title})\n"
        f"🕹 <b>Rejim:</b> {mode_badge}\n"
        f"🗓 <b>Tanishuv:</b> {created_at.strftime('%d.%m.%Y')} ({days_together}-kun birgasiz)\n"
        f"💬 <b>Jami xabarlar:</b> {total_messages} ta\n\n"
        f"🏆 <b>Daraja:</b> {current_level_info['title']}\n"
        f"📈 <b>Ishonch (Trust XP):</b>\n{progress_bar}\n"
    )

    if lvl < 5 and mode == "story":
        next_info = role_levels.get(lvl + 1, {})
        text += f"🎯 <i>Keyingi bosqich ({next_info.get('title', '')}) uchun yana {remaining_xp} XP kerak!</i>\n\n"
    else:
        text += "👑 <i>Siz maksimal yaqinlik va mehr darajasidasiz!</i>\n\n"

    text += (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔐 <b>Ochilgan shaxsiy sirlar:</b> {secrets_count}/5 ta\n"
        f"🧠 <b>Eslab qolingan faktlar:</b> {total_facts} ta\n\n"
        f"<i>Tugmalar orqali to'liq ma'lumotlarni ko'rishingiz mumkin:</i>"
    )

    return text, diary_keyboard()


@diary_router.callback_query(F.data == "diary:secrets")
async def show_secrets_callback(call: CallbackQuery, user: User) -> None:
    """Ochilgan sirlar ro'yxatini ko'rsatish."""
    async with async_session() as session:
        stmt = select(AiProfile).where(AiProfile.user_id == user.id)
        res = await session.execute(stmt)
        profile = res.scalar_one_or_none()

    if not profile:
        await call.answer("Profil topilmadi", show_alert=True)
        return

    unlocked = profile.unlocked_secrets or []
    models = list_character_models(profile.role)
    char_model = get_character_model(profile.role, profile.character_id)

    lines = [
        f"🔐 <b>{profile.ai_name}ning Shaxsiy Sirlari</b>\n",
        "━━━━━━━━━━━━━━━━━━━━━━\n",
    ]

    has_secrets = False
    for m_id, model in models.items():
        sec = model.get("secret_trigger")
        if not sec:
            continue
        has_secrets = True
        sec_id = f"{m_id}_secret"
        is_unlocked = sec_id in unlocked
        title = sec.get("title", "Maxfiy voqea")
        story = sec.get("story", "")

        if is_unlocked:
            lines.append(f"🔓 <b>{title}</b> (Ochilgan):\n<i>«{story}»</i>\n\n")
        else:
            lines.append(f"🔒 <b>{title}</b>: <i>Muloqot orqali ishonch qozonilganda ochiladi</i>\n")

    if not has_secrets:
        lines.append("<i>Hozircha ushbu rol uchun sirlar mavjud emas.</i>\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━\n<i>Ko'proq suhbatlashib, ishonchni oshiring va yangi sirlarni oching!</i>")
    text = "".join(lines)

    await call.message.edit_text(text, reply_markup=back_to_diary_keyboard(), parse_mode="HTML")
    await call.answer()


@diary_router.callback_query(F.data == "diary:facts")
async def show_facts_callback(call: CallbackQuery, user: User) -> None:
    """AI eslab qolgan foydalanuvchi faktlarini ko'rsatish."""
    async with async_session() as session:
        stmt = select(UserFact).where(UserFact.user_id == user.id).order_by(UserFact.updated_at.desc())
        res = await session.execute(stmt)
        facts = res.scalars().all()

    if not facts:
        text = (
            "🧠 <b>Eslab qolingan faktlar xotirasi</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Hozircha xotirada shaxsiy faktlar saqlanmagan.\n"
            "Suhbat davomida ismingiz, kasbingiz, yashash shahringiz yoki yoqtirgan taomingiz "
            "haqida gapirsangiz, AI ularni avtomatik eslab qoladi! ✨"
        )
    else:
        lines = [
            "🧠 <b>Eslab qolingan shaxsiy faktlar</b>\n",
            "━━━━━━━━━━━━━━━━━━━━━━\n",
            "AI ushbu ma'lumotlarni tabiiy suhbatda eslab turadi:\n\n",
        ]
        for f in facts:
            icon = {
                "name": "👤",
                "city": "📍",
                "job": "💼",
                "preference": "🍽",
                "plan": "📅",
            }.get(f.category, "📌")
            lines.append(f"{icon} <b>{f.fact_key}:</b> {f.fact_value}\n")

        lines.append("\n━━━━━━━━━━━━━━━━━━━━━━\n✅ <i>Uzoq muddatli xotira faol va yangilanmoqda.</i>")
        text = "".join(lines)

    await call.message.edit_text(text, reply_markup=back_to_diary_keyboard(), parse_mode="HTML")
    await call.answer()
