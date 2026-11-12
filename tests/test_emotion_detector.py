"""Unit Tests for Emotion Detector and Emotional Prosody."""

import pytest
from voice.emotion_detector import detect_speech_emotion, EMOTION_CONFIGS


def test_detect_romantic_emotion():
    text1 = "Jonim, bugun sizni judayam sog'indim ❤️"
    cfg1 = detect_speech_emotion(text1)
    assert cfg1.name == "romantic"
    assert cfg1.speed <= 0.82  # Sokin, mayin, shoshilmasdan


def test_detect_joyful_emotion():
    text2 = "Haha, juda zo'r gap bo'ldi-ku! 😂🎉"
    cfg2 = detect_speech_emotion(text2)
    assert cfg2.name == "joyful"
    assert cfg2.speed > 0.85  # Quvnoqroq, lekin me'yorida


def test_detect_comforting_emotion():
    text3 = "Xafa bo'lmang, hammasi yaxshi bo'ladi, men yoningizdaman 🥺"
    cfg3 = detect_speech_emotion(text3)
    assert cfg3.name == "comforting"
    assert cfg3.speed <= 0.83


def test_detect_surprised_emotion():
    text4 = "Voy! Nahotki rostdan ham shunaqa bo'ldi?! 😱"
    cfg4 = detect_speech_emotion(text4)
    assert cfg4.name == "surprised"
    assert cfg4.speed > 0.85


def test_detect_calm_default():
    text5 = "Bugun tushlikda uyda o'tirdim va kitob o'qidim."
    cfg5 = detect_speech_emotion(text5)
    assert cfg5.name == "calm"
    assert 0.80 <= cfg5.speed <= 0.86


def test_emotion_configs_complete():
    for name in ["romantic", "joyful", "comforting", "surprised", "calm"]:
        assert name in EMOTION_CONFIGS
        cfg = EMOTION_CONFIGS[name]
        assert 0.75 <= cfg.speed <= 0.95
        assert len(cfg.starter_interjections) > 0
