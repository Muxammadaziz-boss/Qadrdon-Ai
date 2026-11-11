"""Qadirdon AI — Sticker handleri (Business API).

Sticker xabarlarni qabul qiladi va ba'zan emoji reaktsiya bilan javob beradi.
"""

from __future__ import annotations

import random

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
from business.utils.read_receipt import mark_business_message_as_read

sticker_router = Router(name="sticker")

# Sticker ga javob berish ehtimolligi (har doim emas — tabiiy ko'rinishi uchun)
_RESPONSE_CHANCE = 0.6  # 60%

# Javob emojilari
_EMOJI_REACTIONS = ["😄", "😂", "🤣", "❤️", "🔥", "👏", "😍", "🥰", "💪", "👍", "😊", "🫡"]

# Ba'zan matnli javob ham beradi
_TEXT_RESPONSES = [
    "😂😂😂",
    "🤣🤣",
    "Ha ha ha 😄",
    "Zo'r sticker! 😂",
    "👍👍",
    "🔥🔥🔥",
]

# Matnli javob berish ehtimolligi (sticker ga javob berganda)
_TEXT_RESPONSE_CHANCE = 0.3  # 30%


@sticker_router.business_message(F.sticker)
async def handle_business_sticker(message: types.Message, bot: Bot) -> None:
    """Business API orqali kelgan sticker ni qayta ishlaydi.

    Har doim javob bermaydi — tabiiy ko'rinish uchun tasodifiy tanlanadi.
    Ba'zan emoji reaktsiya, ba'zan matn yuboradi.
    """
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

    # Profil egasining o'z xabari bo'lsa o'tkazib yuboramiz
    if message.from_user and message.from_user.id == user.telegram_id:
        return

    ai_profile = await _get_active_ai_profile(user)
    if ai_profile is None or not ai_profile.is_active:
        return

    if not await _check_subscription(user):
        return

    sticker = message.sticker
    sticker_emoji = sticker.emoji if sticker else "?"

    logger.info(
        "Sticker: connection={}, chat={}, emoji={}",
        business_connection_id,
        chat_id,
        sticker_emoji,
    )

    # Kelgan stikerni o'qilgan (✓✓) holatiga o'tkazish
    incoming_message_id = message.message_id
    await mark_business_message_as_read(
        bot=bot,
        business_connection_id=business_connection_id,
        chat_id=chat_id,
        message_id=incoming_message_id,
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

    # Stikerni bazaga saqlash
    await _save_message(
        conversation_id=conversation.id,
        role="user",
        content=f"[Sticker: {sticker_emoji}]",
        message_type="sticker",
    )

    # Tasodifiy ravishda javob berish/bermaslik
    if random.random() > _RESPONSE_CHANCE:
        logger.debug("Sticker ga javob berilmadi (tasodifiy o'tkazib yuborildi)")
        return

    try:
        if random.random() < _TEXT_RESPONSE_CHANCE:
            response = random.choice(_TEXT_RESPONSES)
        else:
            response = random.choice(_EMOJI_REACTIONS)

        await bot.send_message(
            chat_id=chat_id,
            text=response,
            business_connection_id=business_connection_id,
        )

        await mark_business_message_as_read(
            bot=bot,
            business_connection_id=business_connection_id,
            chat_id=chat_id,
            message_id=incoming_message_id,
        )

        await _save_message(
            conversation_id=conversation.id,
            role="assistant",
            content=response,
            message_type="text",
        )
        await _increment_daily_usage(user)

    except Exception as exc:
        logger.error("Sticker javobida xato: {}", exc)
