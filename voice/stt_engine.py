"""Qadirdon AI — Speech-to-Text (STT) dvigatel.

Google Cloud Speech-to-Text API yordamida audio ma'lumotni
matnga aylantiradi. Oddiy va streaming rejimlarini qo'llab-quvvatlaydi.
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator, Optional

try:
    from google.cloud import speech
except ImportError:
    speech = None

from loguru import logger


# ---------------------------------------------------------------------------
# Google STT mijoz
# ---------------------------------------------------------------------------
_client = None


def _get_client():
    """Lazy-init STT async client."""
    global _client
    if speech is None:
        raise RuntimeError("google-cloud-speech kutubxonasi o'rnatilmagan.")
    if _client is None:
        _client = speech.SpeechAsyncClient()
    return _client


def _normalize_language_code(lang: str) -> str:
    """Qisqartirilgan til kodini BCP-47 formatiga o'tkazadi."""
    mapping = {
        "uz": "uz-UZ",
        "ru": "ru-RU",
        "en": "en-US",
        "tr": "tr-TR",
    }
    return mapping.get(lang.lower(), lang)


# ---------------------------------------------------------------------------
# Oddiy (batch) tanib olish
# ---------------------------------------------------------------------------

async def speech_to_text(
    audio_bytes: bytes,
    language: str = "uz",
    sample_rate_hertz: int = 48000,
) -> str:
    """Audio baytlarni matnga aylantiradi.

    Args:
        audio_bytes: Audio ma'lumot (OGG_OPUS yoki LINEAR16).
        language: Til kodi — "uz" yoki "ru".
        sample_rate_hertz: Audio sample rate.

    Returns:
        Tanib olingan matn yoki bo'sh satr.
    """
    language_code = _normalize_language_code(language)

    logger.debug(
        "STT so'rov: lang={}, audio_hajmi={} bayt",
        language_code,
        len(audio_bytes),
    )

    client = _get_client()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=sample_rate_hertz,
        language_code=language_code,
        # Qo'shimcha tillarni ham tanib olishga harakat qiladi
        alternative_language_codes=["ru-RU"] if language_code == "uz-UZ" else ["uz-UZ"],
        enable_automatic_punctuation=True,
        model="latest_long",
    )

    audio = speech.RecognitionAudio(content=audio_bytes)

    response = await client.recognize(config=config, audio=audio)

    if not response.results:
        logger.warning("STT: hech narsa tanib olinmadi")
        return ""

    transcript = " ".join(
        result.alternatives[0].transcript
        for result in response.results
        if result.alternatives
    )

    logger.info("STT natija: {!r}", transcript[:100])
    return transcript.strip()


# ---------------------------------------------------------------------------
# Streaming tanib olish (real-time qo'ng'iroqlar uchun)
# ---------------------------------------------------------------------------

async def stream_speech_to_text(
    audio_stream: AsyncIterator[bytes],
    language: str = "uz",
    sample_rate_hertz: int = 48000,
) -> AsyncIterator[str]:
    """Audio oqimni real-time matnga aylantiradi.

    Bu funksiya streaming recognition yordamida ishlaydi —
    audio kelishi bilan natijalarni qaytaradi.

    Args:
        audio_stream: Audio parchalari oqimi.
        language: Til kodi.
        sample_rate_hertz: Audio sample rate.

    Yields:
        Tanib olingan matn parchalari.
    """
    language_code = _normalize_language_code(language)
    client = _get_client()

    streaming_config = speech.StreamingRecognitionConfig(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate_hertz,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model="latest_long",
        ),
        interim_results=True,
    )

    async def _request_generator():
        """Audio oqimni streaming so'rovlarga aylantiradi."""
        # Birinchi so'rov — konfiguratsiya
        yield speech.StreamingRecognizeRequest(
            streaming_config=streaming_config,
        )
        # Keyingi so'rovlar — audio ma'lumot
        async for chunk in audio_stream:
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    logger.debug("STT streaming boshlandi: lang={}", language_code)

    try:
        responses = await client.streaming_recognize(
            requests=_request_generator(),
        )

        async for response in responses:
            for result in response.results:
                if result.is_final and result.alternatives:
                    transcript = result.alternatives[0].transcript.strip()
                    if transcript:
                        logger.debug("STT stream natija: {!r}", transcript[:80])
                        yield transcript
    except Exception as e:
        logger.error("STT streaming xatolik: {}", e)
        raise
