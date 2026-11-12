"""Unit Tests for Speech Humanizer (Phonetics and Breath Engineering)."""

from voice.speech_humanizer import (
    clean_text_for_speech,
    phonetic_tune_for_uzbek,
    insert_breath_and_pauses,
    inject_speech_interjections,
    humanize_for_speech,
)


def test_clean_text_for_speech():
    text = "**Salom** _dunyo_! `kod` #sarlavha > iqtibos https://t.me/qadirdon 😊 ❤️"
    cleaned = clean_text_for_speech(text)
    assert "**" not in cleaned
    assert "_" not in cleaned
    assert "https://" not in cleaned
    assert "😊" not in cleaned
    assert "Salom dunyo!" in cleaned


def test_clean_text_normalizes_numbers_and_grammar():
    text = "Xatolik chiqibdimi? Soat 14:30 da AI darsimiz bor."
    cleaned = clean_text_for_speech(text)
    assert "chiqdimi" in cleaned
    assert "o'n to'rt o'ttiz" in cleaned
    assert "Ey-Ay" in cleaned


def test_phonetic_tune_for_uzbek():
    text = "Bugun hech narsa bo'lmaydi va ishga kelayotgan edim. Ovqatlandingizmi? Bo'laveradi va aytgan edim."
    tuned = phonetic_tune_for_uzbek(text)
    assert "bo'midi" in tuned
    assert "kelvotuvdim" in tuned
    assert "ovqatlandizmi" in tuned
    assert "bo'loradi" in tuned
    assert "aytgandim" in tuned


def test_insert_breath_and_pauses():
    text = "Bugun charchadim lekin baribir xursandman jonim."
    with_pauses = insert_breath_and_pauses(text)
    assert "... lekin" in with_pauses
    assert "jonim..." in with_pauses


def test_inject_speech_interjections():
    # If text already starts with "Salom", it shouldn't add redundant fillers
    assert inject_speech_interjections("Salom jonim", role="qiz_dost") == "Salom jonim"

    # With probability=1.0, it should add a filler
    res = inject_speech_interjections("Bugun kayfiyatim ajoyib.", role="qiz_dost", probability=1.0)
    assert any(starter in res for starter in ["Hmm...", "Bilasanmi...", "Ha aytgancha...", "Haha..."])


def test_humanize_for_speech_integration():
    text = "Salom! Bugun bo'lmaydi chunki 5 ta ishlarim bor edi."
    res = humanize_for_speech(text, role="qiz_dost")
    assert "bo'midi" in res
    assert "... chunki" in res
    assert "beshta" in res
