"""Unit Tests for Emotion Detector and Emotional Prosody."""

import pytest
from voice.emotion_detector import detect_speech_emotion, EMOTION_CONFIGS


def test_detect_romantic_emotion():
    text1 = "Jonim, bugun sizni judayam sog'indim ❤️"
    cfg1 = detect_speech_emotion(text1)
    assert cfg1.name == "romantic"
    assert cfg1.speed < 1.0  # Sokin, mayin
    assert cfg1.pitch_factor < 1.0  # Yaqin, issiq


def test_detect_joyful_emotion():
    text2 = "Haha, juda zo'r gap bo'ldi-ku! 😂🎉"
    cfg2 = detect_speech_emotion(text2)
    assert cfg2.name == "joyful"
    assert cfg2.speed > 1.0  # Quvnoq, tezroq
    assert cfg2.pitch_factor > 1.0  # Balandroq, yorqin


def test_detect_comforting_emotion():
    text3 = "Xafa bo'lmang, hammasi yaxshi bo'ladi, men yoningizdaman 🥺"
    cfg3 = detect_speech_emotion(text3)
    assert cfg3.name == "comforting"
    assert cfg3.speed < 1.0


def test_detect_surprised_emotion():
    text4 = "Voy! Nahotki rostdan ham shunaqa bo'ldi?! 😱"
    cfg4 = detect_speech_emotion(text4)
    assert cfg4.name == "surprised"
    assert cfg4.speed > 1.0


def test_detect_calm_default():
    text5 = "Bugun tushlikda uyda o'tirdim va kitob o'qidim."
    cfg5 = detect_speech_emotion(text5)
    assert cfg5.name == "calm"
    assert cfg5.speed == 1.00
    assert cfg5.pitch_factor == 1.00


def test_emotion_configs_complete():
    for name in ["romantic", "joyful", "comforting", "surprised", "calm"]:
        assert name in EMOTION_CONFIGS
        cfg = EMOTION_CONFIGS[name]
        assert 0.85 <= cfg.speed <= 1.25
        assert 0.90 <= cfg.pitch_factor <= 1.10
        assert len(cfg.starter_interjections) > 0
