"""Unit tests for Long-Term Memory Fact Extractor."""

import pytest
from ai.memory.fact_extractor import extract_facts_from_text


def test_extract_facts_from_text():
    """O'zbek tilidagi matnlardan shaxsiy faktlar to'g'ri ajratilishini tekshiradi."""
    # 1. Ism
    f1 = extract_facts_from_text("Salom! Mening ismim Jasur, tanishganimdan xursandman.")
    assert any(item["category"] == "name" and item["fact_value"] == "Jasur" for item in f1)

    f1_alt = extract_facts_from_text("Meni Alisher deng xo'pmi?")
    assert any(item["category"] == "name" and item["fact_value"] == "Alisher" for item in f1_alt)

    # 2. Kasb
    f2 = extract_facts_from_text("Men Toshkentda dasturchiman, IT sohasida ishlayman.")
    assert any(item["category"] == "job" and item["fact_value"] == "Dasturchi" for item in f2)

    # 3. Shahar
    f3 = extract_facts_from_text("Men Samarqandda yashayman, qadimiy shahar.")
    assert any(item["category"] == "city" and item["fact_value"] == "Samarqand" for item in f3)

    # 4. Taom / Qiziqish
    f4 = extract_facts_from_text("Sevimli taomim palov, har payshanba yeyman.")
    assert any(item["category"] == "preference" and "Palov" in item["fact_value"] for item in f4)

    # 5. Reja
    f5 = extract_facts_from_text("Ertaga muhim imtihonim bor, duo qilib turing.")
    assert any(item["category"] == "plan" and "imtihonim" in item["fact_value"].lower() for item in f5)


def test_extract_facts_empty():
    """Oddiy gaplardan hech qanday soxta fakt olinmasligini tekshiradi."""
    f = extract_facts_from_text("Salom qalaysiz? Ishlar yaxshimi?")
    assert len(f) == 0
