"""Qadirdon AI — Speech-to-Text (STT) dvigatel.

Google Gemini multimodal AI yordamida audio (ovozli xabar)
ma'lumotlarini matnga aylantiradi (transkripsiya qiladi).
"""

from __future__ import annotations

import asyncio
from google import genai
from google.genai import types
from loguru import logger

from config.settings import settings


async def speech_to_text(
    audio_bytes: bytes,
    language: str = "uz",
    mime_type: str = "audio/ogg",
) -> str:
    """Audio baytlarni matnga aylantiradi (Gemini 2.0 / 3.x Flash orqali).

    Args:
        audio_bytes: Audio fayl baytlari (OGG yoki MP3).
        language: Til kodi ("uz" yoki "ru").
        mime_type: Audio fayl mime-type'i.

    Returns:
        Transkripsiya qilingan matn.
    """
    if not audio_bytes:
        return ""

    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY topilmadi, audio transkripsiyasiz qaytarilmoqda.")
        return ""

    # Normalizing MIME type for Gemini
    m_type = "audio/ogg" if "ogg" in mime_type.lower() else "audio/mp3"

    prompt = (
        "Ushbu audio/ovozli xabardagi gaplarni aynan matn ko'rinishida yozib ber (aniq transkripsiya qil). "
        "Faqat eshitilgan matnni o'zini qaytar, hech qanday qo'shimcha tushuntirish, sarlavha yoki izoh yozma."
    )

    candidate_models = [
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemini-3.1-flash-lite",
    ]

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        for model_name in candidate_models:
            try:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=model_name,
                    contents=[
                        types.Part.from_bytes(data=audio_bytes, mime_type=m_type),
                        prompt,
                    ],
                )
                if response and response.text:
                    text = response.text.strip()
                    logger.info("STT muvaffaqiyatli ({}): {!r}", model_name, text[:80])
                    return text
            except Exception as model_err:
                logger.warning("STT model {} xatosi: {}, keyingi model tekshirilmoqda...", model_name, model_err)
                continue
    except Exception as exc:
        logger.error("STT umumiy xatolik: {}", exc)

    return ""
