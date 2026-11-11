"""Qadirdon AI — Ovozli xabar handleri (Business API).

Telegram Business orqali kelgan ovozli xabarlarni qabul qiladi,
Gemini yordamida matnga aylantiradi, AI javob generatsiya qiladi
va o'zbek ovozi (TTS) bilan haqiqiy ovozli xabar qilib javob yuboradi.
"""

from __future__ import annotations

import io
import os
from pathlib import Path
from aiogram import Bot, F, Router, types
from aiogram.types import FSInputFile
from loguru import logger

from ai.engine import AiEngine
from business.handlers.message import (
    _check_subscription,
    _get_active_ai_profile,
    _get_conversation_history,
    _get_or_create_conversation,
    _get_user_by_business_connection,
    _increment_daily_usage,
    _safe_save_message,
    _save_message,
)
from business.utils.typing_simulator import simulate_recording_voice, simulate_typing
from voice.stt_engine import speech_to_text
from voice.tts_engine import text_to_speech

voice_message_router = Router(name="voice_message")
_ai_engine = AiEngine()


@voice_message_router.business_message(F.voice)
async def handle_business_voice_message(message: types.Message, bot: Bot) -> None:
    """Business API orqali kelgan ovozli xabarni to'liq qayta ishlaydi va ovozli javob beradi."""
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
        "Ovozli xabar keldi: connection={}, chat={}, duration={}s",
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

    # 1. Ovozli faylni yuklab olish va matnga aylantirish (STT)
    transcribed_text = ""
    try:
        file = await bot.get_file(voice.file_id)
        audio_stream = io.BytesIO()
        await bot.download_file(file.file_path, destination=audio_stream)
        audio_bytes = audio_stream.getvalue()

        transcribed_text = await speech_to_text(
            audio_bytes=audio_bytes,
            language="uz",
            mime_type=voice.mime_type or "audio/ogg",
        )
    except Exception as e:
        logger.error("Ovozli xabarni yuklash/transkripsiya qilishda xato: {}", e)

    if not transcribed_text:
        transcribed_text = "[Ovozli xabar eshitildi]"

    logger.info("Transkripsiya natijasi: {!r}", transcribed_text)

    # 2. Xabarlar tarixini olish
    history = await _get_conversation_history(conversation.id)

    # Foydalanuvchi xabarini bazaga saqlash
    await _save_message(
        conversation_id=conversation.id,
        role="user",
        content=transcribed_text,
        message_type="voice",
    )

    # 3. AI javob generatsiya qilish
    try:
        ai_response = await _ai_engine.generate_response(
            user_message=transcribed_text,
            conversation_history=history,
            ai_profile=ai_profile,
            contact_name=contact_name,
        )
        response_text = ai_response["text"]
    except Exception as e:
        logger.error("AI javob generatsiyasida xatolik: {}", e)
        response_text = "Hozir ozroq band edim, nima dedingiz?"

    # 4. Javobni ovozli xabar (TTS) ko'rinishida yuborish
    voice_path = None
    try:
        voice_path = await text_to_speech(
            text=response_text,
            voice_type=getattr(ai_profile, "voice_type", "female_warm"),
            language="uz",
        )

        # Telegramda «ovozli xabar yozmoqda...» effektini ko'rsatish
        await simulate_recording_voice(bot, chat_id, business_connection_id, duration=2.0)

        # Ovozli xabarni jo'natish
        await bot.send_voice(
            chat_id=chat_id,
            voice=FSInputFile(voice_path),
            business_connection_id=business_connection_id,
        )

        await _save_message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            message_type="voice",
        )
        await _increment_daily_usage(user)

    except Exception as exc:
        logger.error("Ovozli javob yuborishda xato: {}, matn ko'rinishida yuborilmoqda", exc)
        # Fallback — matn ko'rinishida yuborish
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
    finally:
        if voice_path and os.path.exists(voice_path):
            Path(voice_path).unlink(missing_ok=True)
