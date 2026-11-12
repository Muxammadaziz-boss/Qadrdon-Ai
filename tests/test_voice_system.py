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


def test_voice_preview_keyboards():
    """Ovoz sozlamalari klaviaturalarida '▶️ Tinglash' tugmasi mavjudligini tekshiradi."""
    from bot.handlers.setup_voice import voice_type_keyboard, VOICE_SAMPLE_PHRASES
    from bot.keyboards.inline import settings_voice_keyboard
    from voice.uzbek_voices import UZBEK_VOICES, resolve_voice_key, get_uzbek_voice

    kb1 = voice_type_keyboard(role="qiz_dost")
    has_preview = any(
        btn.callback_data and btn.callback_data.startswith("preview_voice:")
        for row in kb1.inline_keyboard
        for btn in row
    )
    assert has_preview, "setup_voice klaviaturasida preview_voice tugmasi topilmadi"

    kb2 = settings_voice_keyboard(role="aka")
    has_preview_settings = any(
        btn.callback_data and btn.callback_data.startswith("preview_voice:")
        for row in kb2.inline_keyboard
        for btn in row
    )
    assert has_preview_settings, "settings_voice klaviaturasida preview_voice tugmasi topilmadi"
    assert "lola" in VOICE_SAMPLE_PHRASES
    assert "davron" in VOICE_SAMPLE_PHRASES
    assert resolve_voice_key("female_warm") == "lola"
    assert resolve_voice_key("male_warm") == "davron"
    assert get_uzbek_voice("lola").provider in ("voicelab", "elevenlabs")
    assert get_uzbek_voice("davron").provider == "elevenlabs"


def test_settings_emotion_keyboard():
    """Emotsiya tanlash va tinglash klaviaturasini tekshiradi."""
    from bot.keyboards.inline import settings_emotion_keyboard

    kb = settings_emotion_keyboard(current_emotion="romantic")
    preview_emotions = []
    set_emotions = []

    for row in kb.inline_keyboard:
        for btn in row:
            if btn.callback_data and btn.callback_data.startswith("preview_emotion:"):
                preview_emotions.append(btn.callback_data.split(":")[1])
            elif btn.callback_data and btn.callback_data.startswith("set_emotion:"):
                set_emotions.append(btn.callback_data.split(":")[1])
                if btn.callback_data == "set_emotion:romantic":
                    assert "✅" in btn.text

    assert "auto" in set_emotions
    assert "romantic" in set_emotions
    assert "joyful" in set_emotions
    assert "playful" in set_emotions
    assert "comforting" in set_emotions
    assert "surprised" in set_emotions
    assert "serious" in set_emotions
    assert "calm" in set_emotions

    # All 7 distinct emotions have listen/preview buttons
    for em in ["romantic", "joyful", "playful", "comforting", "surprised", "serious", "calm"]:
        assert em in preview_emotions

