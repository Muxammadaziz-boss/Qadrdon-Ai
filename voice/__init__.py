"""Qadirdon AI — Ovozli qo'ng'iroq moduli.

Bu modul ovozli qo'ng'iroqlar, TTS (Text-to-Speech)
va STT (Speech-to-Text) funksiyalarini boshqaradi.
"""

from voice.tts_engine import text_to_speech
from voice.stt_engine import speech_to_text
from voice.voice_profiles import VOICE_PROFILES

__all__ = [
    "text_to_speech",
    "speech_to_text",
    "VOICE_PROFILES",
]
