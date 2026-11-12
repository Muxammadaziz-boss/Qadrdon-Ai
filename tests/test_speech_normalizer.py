"""Unit Tests for Speech Normalizer (Sentence & Grammar Correction, Numbers, Phonetics)."""

import pytest
from voice.speech_normalizer import (
    clean_markdown_and_system_tags,
    fix_spoken_grammar,
    int_to_uzbek,
    normalize_abbreviations,
    normalize_numbers,
    normalize_uzbek_text_for_speech,
    to_ordinal_uzbek,
    unify_apostrophes,
)


def test_unify_apostrophes():
    text = "oʻzbekiston va gʻalaba hamda moʻjiza"
    res = unify_apostrophes(text)
    assert "o'zbekiston" in res
    assert "g'alaba" in res
    assert "mo'jiza" in res


def test_fix_spoken_grammar():
    # User's explicit test case: "chiqibdimi" -> "chiqdimi"
    text1 = "Voy, xatolik chiqibdimi?"
    assert fix_spoken_grammar(text1) == "Voy, xatolik chiqdimi?"

    # Other spoken grammar corrections
    text2 = "Charchabsizmi va ovqatlanibsizmi?"
    res2 = fix_spoken_grammar(text2)
    assert "Charchadingizmi" in res2
    assert "ovqatlandingizmi" in res2

    text3 = "Ishlar bo'libdimi va xabar kelibdimi?"
    res3 = fix_spoken_grammar(text3)
    assert "bo'ldimi" in res3
    assert "keldimi" in res3


def test_int_to_uzbek():
    assert int_to_uzbek(0) == "nol"
    assert int_to_uzbek(5) == "besh"
    assert int_to_uzbek(15) == "o'n besh"
    assert int_to_uzbek(28) == "yigirma sakkiz"
    assert int_to_uzbek(100) == "yuz"
    assert int_to_uzbek(105) == "yuz besh"
    assert int_to_uzbek(1000) == "ming"
    assert int_to_uzbek(2026) == "ikki ming yigirma olti"
    assert int_to_uzbek(1_000_000) == "bir million"


def test_to_ordinal_uzbek():
    assert to_ordinal_uzbek("bir") == "birinchi"
    assert to_ordinal_uzbek("ikki") == "ikkinchi"
    assert to_ordinal_uzbek("olti") == "oltinchi"
    assert to_ordinal_uzbek("yigirma") == "yigirmanchi"


def test_normalize_numbers_and_time():
    text = "Bugun soat 14:30 da uchrashamiz, 5 ta odam keladi."
    norm = normalize_numbers(text)
    assert "o'n to'rt o'ttiz" in norm
    assert "beshta" in norm

    text_percent = "Bizga 50% chegirma berildi."
    norm_percent = normalize_numbers(text_percent)
    assert "ellik foiz" in norm_percent

    text_year = "2026-yilda IT o'qiymiz."
    norm_year = normalize_numbers(text_year)
    assert "ikki ming yigirma oltinchi yilda" in norm_year


def test_normalize_abbreviations():
    text = "AI va IT sohasida SMS yubordik, OK?"
    norm = normalize_abbreviations(text)
    assert "Ey-Ay" in norm
    assert "Ay-Ti" in norm
    assert "es-em-es" in norm
    assert "oke" in norm


def test_normalize_uzbek_text_for_speech_integration():
    raw = "Xatolik chiqibdimi? 15:30 da AI darsimiz bor, 1-o'rinni olamiz [Ovozli xabar]"
    res = normalize_uzbek_text_for_speech(raw)
    assert "chiqdimi" in res
    assert "o'n besh o'ttiz" in res
    assert "Ey-Ay" in res
    assert "birinchi o'rinni" in res
    assert "[Ovozli xabar]" not in res
