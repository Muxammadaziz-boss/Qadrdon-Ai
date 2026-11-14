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
from voice.speech_humanizer import clean_text_for_speech, humanize_for_speech
from voice.audio_postprocessor import apply_smartphone_voice_filter
from voice.emotion_detector import EmotionConfig, detect_speech_emotion, EMOTION_CONFIGS
from voice.uzbek_voices import get_uzbek_voice, resolve_voice_key, UZBEK_VOICES


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


def _create_temp_audio(suffix: str = ".mp3") -> str:
    """Vaqtinchalik audio fayl yaratadi."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix="qadirdon_voice_")
    os.close(fd)
    return path


_create_temp_mp3 = _create_temp_audio  # Orqaga moslik uchun


async def _tts_voicelab(
    text: str,
    voice_type: str = "",
    role: str = "",
    speed: float = 1.0,
    voice_id_override: str | None = None,
) -> str | None:
    """VoiceLab.uz orqali o'zbek milliy tabiiy ovozini yaratish."""
    api_key = getattr(settings, "VOICELAB_API_KEY", "")
    if not api_key:
        return None

    uz_voice = get_uzbek_voice(voice_type)
    if voice_id_override:
        voice_id = voice_id_override
    elif uz_voice and uz_voice.provider == "voicelab":
        voice_id = uz_voice.voice_id
    else:
        is_female = (
            role in {"qiz_dost", "ayol", "ona", "opa", "singil"}
            or voice_type.startswith("female")
            or voice_type in {"child_playful"}
            or (uz_voice and uz_voice.gender == "female")
        )
        voice_id = (
            getattr(settings, "VOICELAB_VOICE_ID_FEMALE", "voice_EvIb9vE6iY_dWgK7OobYdZcX")
            if is_female
            else getattr(settings, "VOICELAB_VOICE_ID_MALE", "")
        )

    if not voice_id:
        return None

    url = "https://api.voicelab.uz/v1/tts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "audio/wav",
    }
    payload = {
        "text": text,
        "language": "uz",
        "voice_id": voice_id,
        "speed": speed,
    }

    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    audio_data = await resp.read()
                    temp_path = _create_temp_audio(suffix=".wav")
                    Path(temp_path).write_bytes(audio_data)
                    logger.info("VoiceLab.uz TTS muvaffaqiyatli: {} ({} bayt, voice={})", temp_path, len(audio_data), voice_id)
                    return temp_path
                else:
                    err_body = await resp.text()
                    logger.warning("VoiceLab.uz xatosi: status={}, body={}", resp.status, err_body[:120])
    except Exception as exc:
        logger.warning("VoiceLab.uz TTS ulanishida xatolik: {}", exc)

    return None


async def _tts_elevenlabs(text: str, voice_type: str) -> str | None:
    """ElevenLabs Multilingual v2 orqali his-tuyg'uli real inson ovozini yaratish."""
    api_key = getattr(settings, "ELEVENLABS_API_KEY", "")
    if not api_key:
        return None

    uz_voice = get_uzbek_voice(voice_type)
    target_voice_ids: list[str] = []

    # 1. Agar asosiy provider elevenlabs bo'lsa (masalan davron: agoC45V78njTIxYzwmSb)
    if uz_voice and uz_voice.provider == "elevenlabs" and uz_voice.voice_id:
        target_voice_ids.append(uz_voice.voice_id)

    # 2. Har bir milliy ovozning o'ziga xos takrorlanmas ElevenLabs ovozi
    if uz_voice and getattr(uz_voice, "eleven_voice_id", None):
        if uz_voice.eleven_voice_id not in target_voice_ids:
            target_voice_ids.append(uz_voice.eleven_voice_id)

    # 3. Zaxira umumiy ovozlar
    if not target_voice_ids:
        is_female = voice_type.startswith("female") or voice_type in {"child_playful"} or (uz_voice and uz_voice.gender in {"female", "child"})
        default_id = (
            getattr(settings, "ELEVENLABS_VOICE_ID_FEMALE", "cgSgspJ2msm6clMCkdW9")
            if is_female
            else getattr(settings, "ELEVENLABS_VOICE_ID_MALE", "bIHbv24MWmeRgasZH58o")
        )
        target_voice_ids.append(default_id)

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
            for voice_id in target_voice_ids:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        audio_data = await resp.read()
                        temp_path = _create_temp_mp3()
                        Path(temp_path).write_bytes(audio_data)
                        logger.info("ElevenLabs TTS muvaffaqiyatli: {} ({} bayt, voice={})", temp_path, len(audio_data), voice_id)
                        return temp_path
                    else:
                        err_body = await resp.text()
                        logger.warning("ElevenLabs xatosi (voice={}): status={}, body={}", voice_id, resp.status, err_body[:120])
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

    uz_voice = get_uzbek_voice(voice_type)
    if uz_voice and language == "uz":
        voice_name = uz_voice.edge_voice
        pitch_val = int(uz_voice.edge_pitch)
        pitch_str = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"
        rate_percent = int((uz_voice.edge_rate - 1.0) * 100)
        rate_str = f"{'+' if rate_percent >= 0 else ''}{rate_percent}%"
    else:
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
    role: str = "qiz_dost",
    level: int = 1,
    apply_effects: bool = True,
    emotion: str | EmotionConfig | None = None,
    speed_override: float | None = None,
    pitch_override: float | None = None,
    intensity: float = 1.0,
    voice_id_override: str | None = None,
) -> str:
    """Matnni insoniy, fonetik aniq va his-tuyg'uli ovozga aylantiradi.
    
    Bosqichlar:
    1. Emotion Detector: matn mazmuni va parametrlardan hissiy ohangni aniqlaydi (romantik, quvnoq, tasalli, hayrat, sho'x, jiddiy, sokin).
    2. Speech Humanizer & Normalizer: matnni to'liq normalizatsiya qiladi (sonlar, qisqartmalar, apostroflar, jonli grammatika, so'zlashuv fonetikasi va pauzalar).
    3. Multi-provider TTS (VoiceLab.uz -> ElevenLabs -> OpenAI -> Microsoft Edge-TTS) emotsional tezlik va ovoz bilan.
    4. Audio Post-Processor: emotsional ekvalayzer, smartfon mikrofoni filtri va Telegram native Opus (.ogg).
    """
    from dataclasses import replace

    if isinstance(emotion, EmotionConfig):
        emotion_cfg = emotion
    elif isinstance(emotion, str) and emotion in EMOTION_CONFIGS:
        emotion_cfg = EMOTION_CONFIGS[emotion]
    else:
        emotion_cfg = detect_speech_emotion(
            text,
            role=role,
            emotion_override=emotion if isinstance(emotion, str) else None,
            speed_override=speed_override,
            pitch_override=pitch_override,
            intensity=intensity,
        )

    # Agar maxsus override parametrlari berilgan bo'lsa
    if speed_override is not None or pitch_override is not None or intensity != 1.0:
        emotion_cfg = replace(
            emotion_cfg,
            speed=speed_override if speed_override is not None else emotion_cfg.speed,
            pitch_factor=pitch_override if pitch_override is not None else emotion_cfg.pitch_factor,
            intensity=intensity,
        )

    logger.info(
        "Ovoz emotsiyasi tanlandi: {} ({}) | tezlik={:.2f}, pitch={:.2f}, shiddat={:.2f}",
        emotion_cfg.name,
        emotion_cfg.description,
        emotion_cfg.speed,
        emotion_cfg.pitch_factor,
        emotion_cfg.intensity,
    )

    speech_text = humanize_for_speech(text, role=role, level=level, emotion_config=emotion_cfg)
    if not speech_text:
        speech_text = "Salom"

    raw_path: str | None = None
    uz_voice = get_uzbek_voice(voice_type)

    if uz_voice.provider == "elevenlabs":
        raw_path = await _tts_elevenlabs(speech_text, voice_type=voice_type)
        if not raw_path:
            raw_path = await _tts_voicelab(
                speech_text,
                voice_type=voice_type,
                role=role,
                speed=emotion_cfg.speed,
                voice_id_override=voice_id_override,
            )
    else:
        # 1. VoiceLab.uz (O'zbekiston milliy tabiiy AI ovozi)
        raw_path = await _tts_voicelab(
            speech_text,
            voice_type=voice_type,
            role=role,
            speed=emotion_cfg.speed,
            voice_id_override=voice_id_override,
        )
        # 2. Agar VoiceLab balansi tugagan bo'lsa (402), toza o'zbekcha Edge-TTS'ga o'tish
        # (Chunki ElevenLabs umumiy modellari o'zbekchani chet el aksenti bilan aytadi)
        if not raw_path and language == "uz":
            try:
                raw_path = await _tts_edge(speech_text, voice_type=voice_type, language=language)
            except Exception as e:
                logger.warning("Edge-TTS zaxirasi xatosi: {}", e)

        # 3. ElevenLabs
        if not raw_path:
            raw_path = await _tts_elevenlabs(speech_text, voice_type=voice_type)

    # 4. OpenAI TTS
    if not raw_path:
        raw_path = await _tts_openai(speech_text, voice_type=voice_type)

    # 5. Standart bepul Edge-TTS (har doim kafolatlangan zaxira)
    if not raw_path:
        raw_path = await _tts_edge(speech_text, voice_type=voice_type, language=language)

    # 5. Emotsional Smartfon mikrofoni & Telegram Opus filtri
    if apply_effects and raw_path:
        final_path = await apply_smartphone_voice_filter(
            raw_path,
            output_format="ogg",
            emotion_config=emotion_cfg,
        )
        return final_path

    return raw_path
