"""Qadirdon AI — Text-to-Speech (TTS) dvigatel.

Google Cloud Text-to-Speech API yordamida matnni
ovozga aylantiradi va vaqtinchalik audio faylga saqlaydi.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Optional

try:
    from google.cloud import texttospeech
except ImportError:
    texttospeech = None

from loguru import logger

from voice.voice_profiles import DEFAULT_VOICE_TYPE, VOICE_PROFILES, VoiceProfile


# ---------------------------------------------------------------------------
# Google TTS mijozni bir marta yaratamiz (thread-safe)
# ---------------------------------------------------------------------------
_client = None


def _get_client():
    """Lazy-init TTS async client."""
    global _client
    if texttospeech is None:
        raise RuntimeError("google-cloud-texttospeech kutubxonasi o'rnatilmagan.")
    if _client is None:
        _client = texttospeech.TextToSpeechAsyncClient()
    return _client


def _resolve_voice_name(profile: VoiceProfile, language: str) -> str:
    """Til kodiga qarab tegishli voice nomini qaytaradi."""
    if language.startswith("ru"):
        return profile.voice_name_ru
    # O'zbek yoki boshqa tillar uchun
    return profile.voice_name_uz


async def text_to_speech(
    text: str,
    voice_type: str = DEFAULT_VOICE_TYPE,
    language: str = "uz",
) -> str:
    """Matnni ovozga aylantiradi va audio faylga saqlaydi.

    Args:
        text: Aylantirilishi kerak bo'lgan matn.
        voice_type: Ovoz profili nomi (male_warm, male_deep, ...).
        language: Til kodi — "uz" yoki "ru".

    Returns:
        Yaratilgan audio faylning to'liq yo'li (OGG/OPUS formati).

    Raises:
        ValueError: Noto'g'ri voice_type ko'rsatilsa.
        google.api_core.exceptions.GoogleAPIError: TTS API xatosi.
    """
    profile = VOICE_PROFILES.get(voice_type)
    if profile is None:
        raise ValueError(
            f"Noto'g'ri ovoz turi: {voice_type!r}. "
            f"Mavjud turlar: {list(VOICE_PROFILES.keys())}"
        )

    voice_name = _resolve_voice_name(profile, language)
    # Til kodini to'g'rilash (masalan, "uz" → "uz-UZ", "ru" → "ru-RU")
    language_code = _normalize_language_code(language)

    logger.debug(
        "TTS so'rov: voice={}, lang={}, matn_uzunligi={}",
        voice_name,
        language_code,
        len(text),
    )

    client = _get_client()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice_params = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.OGG_OPUS,
        pitch=profile.pitch,
        speaking_rate=profile.speaking_rate,
        volume_gain_db=profile.volume_gain_db,
    )

    response = await client.synthesize_speech(
        input=synthesis_input,
        voice=voice_params,
        audio_config=audio_config,
    )

    # Vaqtinchalik faylga saqlash
    audio_path = await _save_audio(response.audio_content)

    logger.info("TTS tayyor: {} ({} bayt)", audio_path, len(response.audio_content))
    return audio_path


async def _save_audio(audio_bytes: bytes) -> str:
    """Audio kontentni vaqtinchalik faylga saqlaydi.

    Returns:
        Faylning to'liq yo'li.
    """
    loop = asyncio.get_running_loop()

    def _write() -> str:
        fd, path = tempfile.mkstemp(suffix=".ogg", prefix="qadirdon_tts_")
        try:
            with open(fd, "wb") as f:
                f.write(audio_bytes)
        except Exception:
            Path(path).unlink(missing_ok=True)
            raise
        return path

    return await loop.run_in_executor(None, _write)


def _normalize_language_code(lang: str) -> str:
    """Qisqartirilgan til kodini to'liq BCP-47 formatiga o'tkazadi."""
    mapping = {
        "uz": "uz-UZ",
        "ru": "ru-RU",
        "en": "en-US",
        "tr": "tr-TR",
    }
    return mapping.get(lang.lower(), lang)
