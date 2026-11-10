"""Qadirdon AI — /start buyrug'i va Asosiy Menyu.

Foydalanuvchini kutib oladi, bazada tekshiradi.
Yangi bo'lsa — sozlash jarayonini boshlaydi.
Mavjud bo'lsa — asosiy menyuni ko'rsatadi.
"""

from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import func, select

from bot.keyboards.inline import role_keyboard
from bot.keyboards.reply import main_menu_keyboard
from bot.states.setup import SetupStates
from ai.prompts.relationship_levels import get_level_info, get_progress_bar
from config.settings import settings
from db.models import AiProfile, Conversation, Message as DbMessage, User
from db.session import async_session

start_router = Router(name="start")

# ── Rol nomlari (tarjima) ────────────────────────────────────────────────────
ROLE_NAMES = {
    "aka": "👨 Aka",
    "uka": "👦 Uka",
    "opa": "👩 Opa",
    "singil": "👧 Singil",
    "ona": "🤱 Ona",
    "qiz_dost": "💕 Qiz do'st",
    "ayol": "💍 Ayol / Turmush o'rtog'i",
}


def check_is_admin(user_id: int) -> bool:
    """Foydalanuvchi adminmi."""
    return user_id in settings.admin_id_list


@start_router.message(Command("setup"))
@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user: User) -> None:
    """/start yoki /setup buyrug'ini qayta ishlaydi."""
    # Agar /setup chaqirilgan bo'lsa — to'g'ridan-to'g'ri qayta sozlashni boshlaymiz
    is_setup_cmd = message.text and message.text.strip().startswith("/setup")

    # Mavjud AI profilni tekshirish (avval xotiradagi user ob'ektidan)
    profile = user.ai_profiles[0] if user.ai_profiles else None
    if profile is None:
        async with async_session() as session:
            stmt = select(AiProfile).where(AiProfile.user_id == user.id)
            result = await session.execute(stmt)
            profile = result.scalar_one_or_none()

    if profile is None or is_setup_cmd:
        # Yangi foydalanuvchi yoki /setup — ochilish va personaj tanlash
        welcome_text = (
            "🌟 <b>Qadirdon AI — Shaxsiy AI Hamrohingizga xush kelibsiz!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🤖 <b>Qadirdon AI nima?</b>\n"
            "Bu Telegram shaxsiy profilingizda <b>Telegram Business</b> orqali sizning nomingizdan "
            "xuddi haqiqiy insondek muloqot olib boruvchi, o'zaro ishonch (XP) va muloqot darajalariga ega "
            "aqlli virtual hamrohingizdir.\n\n"
            "🎭 <b>Haqiqiy hayotiy personajlar:</b>\n"
            "Tizimda har bir rol uchun tayyor, real o'zbek hayotiy personajlari (o'z ismi, yoshi, kasbi, "
            "kundalik tartibi va o'ziga xos sirlari bilan) mavjud!\n\n"
            "👇 <b>Boshlash uchun personaj rolini tanlang:</b>"
        )
        await message.answer(
            welcome_text,
            reply_markup=role_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(SetupStates.choosing_role)
    else:
        # Mavjud foydalanuvchi — asosiy menyu
        role_display = ROLE_NAMES.get(profile.role, profile.role)
        status_emoji = "🟢" if profile.is_active else "🔴"
        status_text = "Faol" if profile.is_active else "O'chirilgan"

        business_status = (
            "🟢 Ulangan" if user.business_connection_id else "🔴 Ulanmagan"
        )

        level = getattr(profile, "relationship_level", 1)
        xp = getattr(profile, "trust_xp", 0)
        mode = getattr(profile, "game_mode", "story")
        level_info = get_level_info(profile.role, level)
        mode_text = "🎮 Zabt etish" if mode == "story" else "🌟 Klassik"
        progress_text = get_progress_bar(xp, level)

        menu_text = (
            f"👋 <b>Salom, {user.full_name or 'do\'stim'}!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🤖 <b>AI Ismi:</b> {profile.ai_name}\n"
            f"🎭 <b>Rol:</b> {role_display}\n"
            f"❤️ <b>Munosabat:</b> {level_info['title']}\n"
            f"📊 <b>Ishonch:</b> {progress_text}\n"
            f"🕹 <b>Rejim:</b> {mode_text}\n"
            f"{status_emoji} <b>AI Holati:</b> {status_text}\n"
            f"📱 <b>Telegram Business:</b> {business_status}\n"
            f"💳 <b>Balans:</b> {user.balance:,} so'm\n\n"
            "📌 Quyidagi menyudan kerakli bo'limni tanlang:"
        )
        await message.answer(
            menu_text,
            reply_markup=main_menu_keyboard(
                is_admin=check_is_admin(user.telegram_id)
            ),
            parse_mode="HTML",
        )
        await state.clear()


@start_router.message(F.text == "📊 Statistika")
async def show_user_stats(message: Message, user: User) -> None:
    """Foydalanuvchining shaxsiy statistikasini ko'rsatadi."""
    async with async_session() as session:
        # Suhbatlar soni
        conv_count = (
            await session.scalar(
                select(func.count(Conversation.id)).where(
                    Conversation.user_id == user.id
                )
            )
            or 0
        )

        # Xabarlar soni
        msg_count = (
            await session.scalar(
                select(func.count(DbMessage.id))
                .join(Conversation, DbMessage.conversation_id == Conversation.id)
                .where(Conversation.user_id == user.id)
            )
            or 0
        )

    text = (
        "📊 <b>Sizning Shaxsiy Statistikangiz:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💬 <b>Siz nomingizdan gaplashilgan suhbatlar:</b> {conv_count} ta\n"
        f"✉️ <b>AI yozgan jami xabarlar:</b> {msg_count} ta\n"
        f"💳 <b>Joriy hisob balansingiz:</b> {user.balance:,} so'm\n\n"
        "<i>Qadirdon AI profilingizda 24/7 sizning yaqinlaringiz bilan samimiy suhbatlashadi.</i>"
    )
    await message.answer(text, parse_mode="HTML")


@start_router.message(F.text == "ℹ️ Yordam")
async def show_help(message: Message) -> None:
    """Yordam va qo'llanma matni."""
    text = (
        "ℹ️ <b>Qadirdon AI — Foydalanish Yo'riqnomasi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>1. AI Shaxsini Sozlash:</b>\n"
        "• '⚙️ Sozlamalar' bo'limiga kiring.\n"
        "• AI rolining turini (Aka, Uka, Singil, Ona, Qiz do'st, Ayol) va ismini tanlang.\n"
        "• Emoji darajasi va yozish tezligini o'zingizga moslang.\n\n"
        "<b>2. Telegram Business Profilga Ulash:</b>\n"
        "• Telegram ilovangizda: <b>Sozlamalar</b> ➡️ <b>Telegram Business</b> ➡️ <b>Chat-botlar (Chatbots)</b>.\n"
        "• Ushbu botning username'ini kiriting va ruxsat bering.\n"
        "• Shundan so'ng profilingizga kelgan xabarlarga AI avtomatik javob bera boshlaydi!\n\n"
        "<b>3. Balans va Tariflar:</b>\n"
        "• '💰 Balans va Tariflar' bo'limi orqali hisobingizni ko'rishingiz va tariflarni xarid qilishingiz mumkin.\n"
        f"• Savollar bo'lsa: {settings.ADMIN_USERNAME} ga yozing."
    )
    await message.answer(text, parse_mode="HTML")
