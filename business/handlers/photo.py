"""Qadirdon AI — Rasm (foto) handleri (Business API).

Rasm xabarlarni qabul qiladi va AI rolga mos javob beradi.
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

photo_router = Router(name="photo")

# Rolga qarab foto uchun javoblar
_PHOTO_RESPONSES: dict[str, str] = {
    "aka": "Rasm yuboribsiz-ku! 📸 Zo'r ko'rinadi, ukaginam!",
    "uka": "Voy, qanday rasm! 📷 Ko'rish yoqdi, akaginam!",
    "opa": "Chiroyli rasm ekan! 🤩 Rahmat yuborganingiz uchun!",
    "singil": "Oh, qanday ajoyib! 📸 Juda yoqdi!",
    "ona": "Bolam, chiroyli rasm yuboribsan! 🥰 Sog'-omonmisan?",
    "qiz_dost": "Voy, juda chiroyli! 😍 Yana yuboring!",
    "ayol": "Rasm uchun rahmat, azizim! 💕",
}

_DEFAULT_PHOTO_RESPONSE = "Rasmingiz uchun rahmat! 📸 Yoqdi!"


@photo_router.business_message(F.photo)
async def handle_business_photo(message: types.Message, bot: Bot) -> None:
    """Business API orqali kelgan rasmni qayta ishlaydi.

    AI rolga mos javob yuboradi.
    """
    business_connection_id = message.business_connection_id
    chat_id = message.chat.id

    if not business_connection_id:
        return

    # Faqat shaxsiy (private) chatlar
    if message.chat.type != "private":
        return

    # Foydalanuvchini topish
    user = await _get_user_by_business_connection(business_connection_id)
    if user is None:
        return

    # Profil egasining o'z xabari bo'lsa javob bermaymiz (self-reply protection)
    if message.from_user and message.from_user.id == user.telegram_id:
        return

    # Faol AI profil
    ai_profile = await _get_active_ai_profile(user)
    if ai_profile is None or not ai_profile.is_active:
        return

    # Obuna limitini tekshirish
    if not await _check_subscription(user):
        return

    logger.info(
        "Rasm xabari: connection={}, chat={}",
        business_connection_id,
        chat_id,
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

    # Rasm xabarini bazaga saqlash
    photo_desc = f"[Rasm] {message.caption}" if message.caption else "[Rasm]"
    await _save_message(
        conversation_id=conversation.id,
        role="user",
        content=photo_desc,
        message_type="photo",
    )

    response_text = _PHOTO_RESPONSES.get(ai_profile.role, _DEFAULT_PHOTO_RESPONSE)
    typing_speed = ai_profile.typing_speed

    # Caption bo'lsa, qo'shimcha qilish
    if message.caption:
        response_text += f"\n\n«{message.caption}» — zo'r sarlavha! 👍"

    try:
        await simulate_typing(
            bot, chat_id, business_connection_id, response_text,
            typing_speed=typing_speed,
        )
        await bot.send_message(
            chat_id=chat_id,
            text=response_text,
            business_connection_id=business_connection_id,
        )

        # AI javobini saqlash va limitni oshirish
        await _save_message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            message_type="text",
        )
        await _increment_daily_usage(user)

    except Exception as exc:
        logger.error("Rasm javobida xato: {}", exc)
