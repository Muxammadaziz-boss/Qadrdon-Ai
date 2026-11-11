"""Qadirdon AI — Text-to-Speech (TTS) dvigatel.

Multi-provider arxitektura:
1. ElevenLabs Multilingual v2 (O'ta realistik, nafas olish, kulgi, his-tuyg'ular) — agar API kalit bo'lsa.
2. OpenAI TTS (tts-1-hd) — agar OpenAI API kalit bo'lsa.
3. Microsoft Edge-TTS Neural (100% bepul, tezkor, optimallashgan o'zbekcha) — standart fallback.
"""

from __future__ import annotations

import asyncio
import os
import re
import tempfile
from pathlib import Path

import aiohttp
from loguru import logger

try:
    import edge_tts
except ImportError:
    edge_tts = None

from config.settings import settings
from voice.voice_profiles import DEFAULT_VOICE_TYPE, VOICE_PROFILES, VoiceProfile


def clean_text_for_speech(text: str) -> str:
    """Ovozga aylantirishdan oldin matnni tabiiy talaffuz uchun tozalaydi."""
    if not text:
        return ""
    # Markdown belgilarini tozalash (*kursiv*, **qalin**, `kod`, # sarlavha)
    cleaned = re.sub(r"[*_~`#>]", "", text)
    # URL manzillarni tozalash
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    # Emojilarni tozalash
    emoji_pattern = re.compile(
        r"[\U00010000-\U0010ffff]|[\u2000-\u32ff]|[\ud83c-\ud83e][\ud000-\udfff]",
        flags=re.UNICODE,
    )
    cleaned = emoji_pattern.sub("", cleaned)
    # Ko'p nuqtalarni tabiiy pauza uchun bitta nuqtaga aylantirish
    cleaned = re.sub(r"\.{2,}", "...", cleaned)
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


def _create_temp_mp3() -> str:
    """Vaqtinchalik MP3 fayl yaratadi."""
    fd, path = tempfile.mkstemp(suffix=".mp3", prefix="qadirdon_voice_")
    os.close(fd)
    return path


async def _tts_elevenlabs(text: str, voice_type: str) -> str | None:
    """ElevenLabs Multilingual v2 orqali his-tuyg'uli real inson ovozini yaratish."""
    api_key = getattr(settings, "ELEVENLABS_API_KEY", "")
    if not api_key:
        return None

    is_female = voice_type.startswith("female") or voice_type in {"child_playful"}
    voice_id = (
        getattr(settings, "ELEVENLABS_VOICE_ID_FEMALE", "cgSgspJ2msm6clMCkdW9")
        if is_female
        else getattr(settings, "ELEVENLABS_VOICE_ID_MALE", "iP95p4xoKVk53GoZ742B")
    )

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.40,
            "similarity_boost": 0.85,
            "style": 0.35,
            "use_speaker_boost": True,
        },
    }

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    audio_data = await resp.read()
                    temp_path = _create_temp_mp3()
                    Path(temp_path).write_bytes(audio_data)
                    logger.info("ElevenLabs TTS muvaffaqiyatli: {} ({} bayt)", temp_path, len(audio_data))
                    return temp_path
                else:
                    err_body = await resp.text()
                    logger.warning("ElevenLabs xatosi: status={}, body={}", resp.status, err_body[:120])
    except Exception as exc:
        logger.warning("ElevenLabs TTS ulanishida xatolik: {}", exc)

    return None


async def _tts_openai(text: str, voice_type: str) -> str | None:
    """OpenAI TTS orqali audio yaratish."""
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        return None

    is_female = voice_type.startswith("female") or voice_type in {"child_playful"}
    voice_name = "nova" if is_female else "onyx"

    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "tts-1-hd",
        "input": text,
        "voice": voice_name,
    }

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    audio_data = await resp.read()
                    temp_path = _create_temp_mp3()
                    Path(temp_path).write_bytes(audio_data)
                    logger.info("OpenAI TTS muvaffaqiyatli: {} ({} bayt)", temp_path, len(audio_data))
                    return temp_path
                else:
                    err_body = await resp.text()
                    logger.warning("OpenAI TTS xatosi: status={}, body={}", resp.status, err_body[:120])
    except Exception as exc:
        logger.warning("OpenAI TTS ulanishida xatolik: {}", exc)

    return None


async def _tts_edge(text: str, voice_type: str, language: str) -> str:
    """Bepul Microsoft Edge-TTS orqali ovoz yaratish."""
    if edge_tts is None:
        raise RuntimeError("edge-tts kutubxonasi o'rnatilmagan.")

    profile = VOICE_PROFILES.get(voice_type, VOICE_PROFILES.get(DEFAULT_VOICE_TYPE))
    voice_name = _resolve_edge_voice(profile, language)
    rate_str, pitch_str = _format_rate_and_pitch(profile)

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice_name,
        rate=rate_str,
        pitch=pitch_str,
    )

    loop = asyncio.get_running_loop()
    temp_path = await loop.run_in_executor(None, _create_temp_mp3)

    try:
        await communicate.save(temp_path)
        logger.info("Edge-TTS tayyor: {} ({} bayt)", temp_path, os.path.getsize(temp_path))
        return temp_path
    except Exception as e:
        Path(temp_path).unlink(missing_ok=True)
        logger.error("Edge-TTS generatsiya qilishda xatolik: {}", e)
        raise


async def text_to_speech(
    text: str,
    voice_type: str = DEFAULT_VOICE_TYPE,
    language: str = "uz",
) -> str:
    """Matnni ovozga aylantiradi.
    
    Ketma-ketlik:
    1. ElevenLabs (agar ELEVENLABS_API_KEY bo'lsa — haqiqiy inson his-tuyg'ulari)
    2. OpenAI TTS (agar OPENAI_API_KEY bo'lsa)
    3. Microsoft Edge-TTS (har doim bepul va tayyor)
    """
    cleaned_text = clean_text_for_speech(text)
    if not cleaned_text:
        cleaned_text = "Salom"

    # 1. ElevenLabs (O'ta hissiyotli inson ovozi)
    el_path = await _tts_elevenlabs(cleaned_text, voice_type=voice_type)
    if el_path:
        return el_path

    # 2. OpenAI TTS
    oa_path = await _tts_openai(cleaned_text, voice_type=voice_type)
    if oa_path:
        return oa_path

    # 3. Standart bepul Edge-TTS
    return await _tts_edge(cleaned_text, voice_type=voice_type, language=language)
