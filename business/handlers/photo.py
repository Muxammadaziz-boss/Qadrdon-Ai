"""Qadirdon AI — Rasm (foto) handleri (Business API).

Multimodal Gemini Vision yordamida foydalanuvchi yuborgan fotosuratlarni
chuqur tahlil qilib, personaj nomidan real vaqtda samimiy, insoniy munosabat bildirish.
"""

from __future__ import annotations

import asyncio
import io
import random
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
    _safe_increment_daily_usage,
    _safe_save_message,
    _safe_update_relationship,
)
from business.utils.human_delay import calculate_delay
from business.utils.read_receipt import mark_business_message_as_read
from business.utils.typing_simulator import simulate_recording_voice, simulate_typing
from voice.tts_engine import text_to_speech

photo_router = Router(name="photo")
_ai_engine = AiEngine()

# Offline yoki kutilmagan fallback holati uchun javoblar
_PHOTO_FALLBACKS: dict[str, str] = {
    "aka": "Rasm yuboribsiz-ku! 📸 Zo'r ko'rinadi, ukaginam!",
    "uka": "Voy, qanday rasm! 📷 Ko'rish yoqdi, akaginam!",
    "opa": "Chiroyli rasm ekan! 🤩 Rahmat yuborganingiz uchun!",
    "singil": "Oh, qanday ajoyib! 📸 Juda yoqdi!",
    "ona": "Bolam, chiroyli rasm yuboribsan! 🥰 Sog'-omonmisan?",
    "qiz_dost": "Voy, buncha chiroyli! 😍 Judayam yoqdi!",
    "ayol": "Rasm uchun rahmat, azizim! 💕",
}
_DEFAULT_FALLBACK = "Rasmingiz uchun rahmat! 📸 Juda yoqdi!"


@photo_router.business_message(F.photo)
async def handle_business_photo(message: types.Message, bot: Bot) -> None:
    """Business API orqali kelgan rasmni multimodal AI orqali tahlil qiladi va javob beradi."""
    business_connection_id = message.business_connection_id
    chat_id = message.chat.id

    if not business_connection_id or message.chat.type != "private":
        return

    # 1. Foydalanuvchi va AI profilini aniqlash
    user = await _get_user_by_business_connection(business_connection_id)
    if user is None:
        return

    # Profil egasining o'z xabari bo'lsa javob bermaymiz
    if message.from_user and message.from_user.id == user.telegram_id:
        return

    ai_profile = await _get_active_ai_profile(user)
    if ai_profile is None or not ai_profile.is_active:
        return

    if not await _check_subscription(user):
        return

    incoming_message_id = message.message_id
    logger.info("Rasm xabari qabul qilindi: connection={}, chat={}", business_connection_id, chat_id)

    # 2. Kelgan xabarni o'qilgan (double true / ✓✓) holatiga o'tkazish
    await mark_business_message_as_read(
        bot=bot,
        business_connection_id=business_connection_id,
        chat_id=chat_id,
        message_id=incoming_message_id,
    )

    # 3. Suhbatni olish / yaratish
    contact_name = ""
    if message.from_user:
        contact_name = message.from_user.full_name or message.from_user.first_name or ""

    conversation = await _get_or_create_conversation(
        user=user,
        contact_chat_id=chat_id,
        contact_name=contact_name,
        business_connection_id=business_connection_id,
    )

    caption_text = (message.caption or "").strip()
    photo_desc = f"[Rasm] {caption_text}" if caption_text else "[Rasm]"

    # 4. Foydalanuvchi xabarini bazaga saqlash
    asyncio.create_task(
        _safe_save_message(
            conversation_id=conversation.id,
            role="user",
            content=photo_desc,
            message_type="photo",
        )
    )

    # 5. Rasm faylini xotiraga (baytlarga) yuklab olish
    image_bytes: bytes | None = None
    try:
        photo_size = message.photo[-1]
        buffer = io.BytesIO()
        await bot.download(photo_size, destination=buffer)
        image_bytes = buffer.getvalue()
        logger.info("Rasm muvaffaqiyatli yuklab olindi ({} bayt)", len(image_bytes))
    except Exception as d_err:
        logger.warning("Rasm yuklab olishda xatolik: {}", d_err)

    # 6. Suhbat tarixi
    history = await _get_conversation_history(conversation.id)

    # 7. Gemini Vision orqali rasmni tahlil qilib javob yaratish
    try:
        ai_response = await _ai_engine.generate_response(
            user_message=caption_text,
            conversation_history=history,
            ai_profile=ai_profile,
            contact_name=contact_name,
            image_bytes=image_bytes,
            image_mime_type="image/jpeg",
        )
        response_text = ai_response.get("text", "")
        parts = ai_response.get("parts", [response_text])
        delay_seconds = ai_response.get("delay_seconds", 0.0)
        correction = ai_response.get("correction")
    except Exception as e:
        logger.error("Rasm tahlilida Gemini xatosi: {}", e)
        response_text = _PHOTO_FALLBACKS.get(ai_profile.role, _DEFAULT_FALLBACK)
        if caption_text:
            response_text += f"\n\n«{caption_text}» 👍"
        parts = [response_text]
        delay_seconds = 0.5
        correction = None

    if delay_seconds > 0:
        await asyncio.sleep(min(delay_seconds, 1.0))

    # 8. Ovozli yoki matnli javob yuborish
    VOICE_KEYWORDS = ("ovozli", "ovozing", "audio", "gapir", "eshitay")
    user_asked_voice = any(kw in caption_text.lower() for kw in VOICE_KEYWORDS)
    voice_enabled = getattr(ai_profile, "voice_enabled", False)
    should_send_voice = user_asked_voice or (voice_enabled and random.random() < 0.35)
    voice_sent = False

    if should_send_voice:
        try:
            voice_path = await text_to_speech(
                text=response_text,
                voice_type=getattr(ai_profile, "voice_type", "female_warm"),
                language="uz",
                role=getattr(ai_profile, "role", "qiz_dost"),
                level=getattr(ai_profile, "relationship_level", 1),
            )
            record_duration = max(1.5, min(3.5, len(response_text) * 0.04))
            await simulate_recording_voice(bot, chat_id, business_connection_id, duration=record_duration)

            await bot.send_voice(
                chat_id=chat_id,
                voice=FSInputFile(voice_path),
                business_connection_id=business_connection_id,
            )
            full_response = f"[Ovozli xabar: {response_text}]"
            voice_sent = True
            Path(voice_path).unlink(missing_ok=True)
            logger.info("Rasmga ovozli javob yuborildi: user_id={}, chat_id={}", user.id, chat_id)
        except Exception as v_err:
            logger.warning("Rasmga ovozli javobda xato: {}, matnga o'tilmoqda: {}", v_err)
            voice_sent = False

    try:
        if not voice_sent:
            if len(parts) > 1 and getattr(ai_profile, "message_splitting", True):
                for i, part in enumerate(parts):
                    await simulate_typing(
                        bot, chat_id, business_connection_id, part,
                        typing_speed=ai_profile.typing_speed,
                    )
                    await bot.send_message(
                        chat_id=chat_id,
                        text=part,
                        business_connection_id=business_connection_id,
                    )
                    if i < len(parts) - 1:
                        inter_delay = calculate_delay(
                            text_length=len(parts[i + 1]),
                            typing_speed=ai_profile.typing_speed,
                        )
                        await asyncio.sleep(min(inter_delay, 1.0))
                full_response = "\n".join(parts)
            else:
                await simulate_typing(
                    bot, chat_id, business_connection_id, response_text,
                    typing_speed=ai_profile.typing_speed,
                )
                await bot.send_message(
                    chat_id=chat_id,
                    text=response_text,
                    business_connection_id=business_connection_id,
                )
                full_response = response_text

            if correction:
                await asyncio.sleep(0.6)
                await bot.send_message(
                    chat_id=chat_id,
                    text=correction,
                    business_connection_id=business_connection_id,
                )
                full_response += f"\n{correction}"

    except Exception as send_err:
        logger.error("Rasm javobini yuborishda xato: {}", send_err)
        return

    # Qayta o'qildi (✓✓) holatiga o'tkazish
    await mark_business_message_as_read(
        bot=bot,
        business_connection_id=business_connection_id,
        chat_id=chat_id,
        message_id=incoming_message_id,
    )

    # 9. Bazaga saqlash, kunlik hisoblagichni oshirish va munosabatni rivojlantirish
    asyncio.create_task(
        _safe_save_message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response,
            message_type="text",
        )
    )
    asyncio.create_task(_safe_increment_daily_usage(user))
    asyncio.create_task(
        _safe_update_relationship(
            user=user,
            ai_profile=ai_profile,
            user_text=f"Rasm yubordi: {caption_text}" if caption_text else "Rasm yubordi",
            bot=bot,
        )
    )

    logger.info("Rasmga javob muvaffaqiyatli yuborildi: user_id={}, chat_id={}", user.id, chat_id)
