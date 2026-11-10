"""Qadirdon AI — Ovozli xabar handleri (Business API).

Ovozli xabarlarni qabul qiladi va xavfsiz javob qaytaradi.
"""

from __future__ import annotations

from aiogram import Bot, F, Router, types
from loguru import logger

from business.handlers.message import (
    _check_subscription,
    _get_active_ai_profile,
    _get_or_create_conversation,
    _get_user_by_business_connection,
    _increment_daily_usage,
    _save_message,
)
from business.utils.typing_simulator import simulate_typing

voice_message_router = Router(name="voice_message")


@voice_message_router.business_message(F.voice)
async def handle_business_voice_message(message: types.Message, bot: Bot) -> None:
    """Business API orqali kelgan ovozli xabarni qayta ishlaydi."""
    business_connection_id = message.business_connection_id
    chat_id = message.chat.id

    if not business_connection_id:
        return

    # Faqat shaxsiy chat
    if message.chat.type != "private":
        return

    user = await _get_user_by_business_connection(business_connection_id)
    if user is None:
        return

    # Profil egasining o'z xabari bo'lsa o'tkazib yuboramiz (self-reply protection)
    if message.from_user and message.from_user.id == user.telegram_id:
        return

    ai_profile = await _get_active_ai_profile(user)
    if ai_profile is None or not ai_profile.is_active:
        return

    if not await _check_subscription(user):
        return

    voice = message.voice
    duration = voice.duration if voice else 0

    logger.info(
        "Ovozli xabar: connection={}, chat={}, duration={}s",
        business_connection_id,
        chat_id,
        duration,
    )

    contact_name = ""
    if message.from_user:
        contact_name = message.from_user.full_name or message.from_user.first_name or ""

    conversation = await _get_or_create_conversation(
        user=user,
        contact_chat_id=chat_id,
        contact_name=contact_name,
        business_connection_id=business_connection_id,
    )

    # Ovozli xabarni saqlash
    await _save_message(
        conversation_id=conversation.id,
        role="user",
        content=f"[Ovozli xabar: {duration} soniya]",
        message_type="voice",
    )

    response_text = (
        "Ovozli xabaringizni eshitdim! 🎧 "
        "Hozircha ovozli xabarlarni matn sifatida to'liq qayta ishlay olmayman, "
        "iltimos, iloji bo'lsa matn ko'rinishida yozing. ✍️"
    )

    try:
        await simulate_typing(
            bot, chat_id, business_connection_id, response_text,
            typing_speed=ai_profile.typing_speed,
        )
        await bot.send_message(
            chat_id=chat_id,
            text=response_text,
            business_connection_id=business_connection_id,
        )

        await _save_message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            message_type="text",
        )
        await _increment_daily_usage(user)

    except Exception as exc:
        logger.error("Ovozli xabar javobida xato: {}", exc)
