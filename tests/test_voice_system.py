"""Voice System Unit Tests — TTS and Voice Profiles."""

import os
import pytest
from voice.voice_profiles import VOICE_PROFILES, DEFAULT_VOICE_TYPE
from voice.tts_engine import clean_text_for_speech, text_to_speech


def test_voice_profiles_complete():
    """Barcha ovoz profillari to'liq mavjudligini tekshiradi."""
    expected_voices = [
        "male_warm", "male_deep", "female_soft", "female_warm",
        "female_bright", "female_calm", "male_calm", "male_energetic",
        "child_playful",
    ]
    for key in expected_voices:
        assert key in VOICE_PROFILES
        prof = VOICE_PROFILES[key]
        assert prof.voice_name_uz
        assert prof.voice_name_ru
        assert isinstance(prof.pitch, (int, float))
        assert isinstance(prof.speaking_rate, (int, float))


def test_clean_text_for_speech():
    """Ovozga aylantirishdan oldin matn tozalanishini tekshiradi."""
    raw = "*Salom*, **dunyo**! `kod` https://google.com 😊 ❤️ ✨ Yaxshimisiz?"
    cleaned = clean_text_for_speech(raw)
    assert "*" not in cleaned
    assert "`" not in cleaned
    assert "https://" not in cleaned
    assert "😊" not in cleaned
    assert "❤️" not in cleaned
    assert "Salom, dunyo!" in cleaned
    assert "Yaxshimisiz?" in cleaned


def test_text_to_speech_generates_file():
    """TTS ovozli fayl (.mp3) generatsiya qilishini tekshiradi."""
    import asyncio
    path = asyncio.run(text_to_speech("Salom, bu test xabari.", voice_type="female_warm", language="uz"))
    try:
        assert os.path.exists(path)
        assert os.path.getsize(path) > 1000
    finally:
        if os.path.exists(path):
            os.remove(path)
