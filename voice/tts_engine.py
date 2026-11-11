"""Qadirdon AI — Text-to-Speech (TTS) dvigatel.

Edge-TTS (Microsoft Neural) yordamida matnni tabiiy o'zbek
va ruscha ovozga aylantiradi va audio faylga saqlaydi.
"""

from __future__ import annotations

import asyncio
import os
import re
import tempfile
from pathlib import Path
from loguru import logger

try:
    import edge_tts
except ImportError:
    edge_tts = None

from voice.voice_profiles import DEFAULT_VOICE_TYPE, VOICE_PROFILES, VoiceProfile


def clean_text_for_speech(text: str) -> str:
    """Ovozga aylantirishdan oldin matnni keraksiz belgilardan tozalaydi."""
    if not text:
        return ""
    # Markdown belgilarini tozalash (*kursiv*, **qalin**, `kod`, # sarlavha)
    cleaned = re.sub(r"[*_~`#>]", "", text)
    # URL manzillarni tozalash
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    # Emojilarni tozalash (TTS g'alati o'qimasligi uchun)
    emoji_pattern = re.compile(
        r"[\U00010000-\U0010ffff]|[\u2000-\u32ff]|[\ud83c-\ud83e][\ud000-\udfff]",
        flags=re.UNICODE,
    )
    cleaned = emoji_pattern.sub("", cleaned)
    # Ortiqcha probellarni qisqartirish
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _resolve_edge_voice(profile: VoiceProfile, language: str) -> str:
    """Til kodiga qarab tegishli Edge-TTS ovoz nomini qaytaradi."""
    if language.startswith("ru"):
        return profile.voice_name_ru
    return profile.voice_name_uz


def _format_rate_and_pitch(profile: VoiceProfile) -> tuple[str, str]:
    """Profile parametrlarini Edge-TTS formatiga o'tkazadi."""
    rate_val = int((profile.speaking_rate - 1.0) * 100)
    rate_str = f"{'+' if rate_val >= 0 else ''}{rate_val}%"

    pitch_val = int(profile.pitch)
    pitch_str = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"

    return rate_str, pitch_str


async def text_to_speech(
    text: str,
    voice_type: str = DEFAULT_VOICE_TYPE,
    language: str = "uz",
) -> str:
    """Matnni ovozga aylantiradi va audio fayl (.mp3) yo'lini qaytaradi.

    Args:
        text: Aylantirilishi kerak bo'lgan matn.
        voice_type: Ovoz profili nomi (female_warm, male_warm, ...).
        language: Til kodi ("uz" yoki "ru").

    Returns:
        Yaratilgan audio faylning to'liq yo'li.
    """
    cleaned_text = clean_text_for_speech(text)
    if not cleaned_text:
        cleaned_text = "Salom"

    profile = VOICE_PROFILES.get(voice_type, VOICE_PROFILES.get(DEFAULT_VOICE_TYPE))
    voice_name = _resolve_edge_voice(profile, language)
    rate_str, pitch_str = _format_rate_and_pitch(profile)

    logger.debug(
        "TTS boshlandi: voice={}, rate={}, pitch={}, len={}",
        voice_name, rate_str, pitch_str, len(cleaned_text),
    )

    if edge_tts is None:
        raise RuntimeError("edge-tts kutubxonasi o'rnatilmagan.")

    communicate = edge_tts.Communicate(
        text=cleaned_text,
        voice=voice_name,
        rate=rate_str,
        pitch=pitch_str,
    )

    # Vaqtinchalik audio fayl yaratish (.mp3)
    loop = asyncio.get_running_loop()
    def _create_temp() -> str:
        fd, path = tempfile.mkstemp(suffix=".mp3", prefix="qadirdon_voice_")
        os.close(fd)
        return path

    temp_path = await loop.run_in_executor(None, _create_temp)

    try:
        await communicate.save(temp_path)
        logger.info("TTS tayyor: {} ({} bayt)", temp_path, os.path.getsize(temp_path))
        return temp_path
    except Exception as e:
        Path(temp_path).unlink(missing_ok=True)
        logger.error("TTS generatsiya qilishda xatolik: {}", e)
        raise
