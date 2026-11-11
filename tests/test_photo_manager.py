"""Unit tests for Character Photos and Atmosphere Gallery."""

import pytest
from ai.characters.photo_manager import (
    is_photo_requested,
    get_photo_category,
    get_photo_caption,
    ATMOSPHERE_GALLERY,
)


def test_is_photo_requested():
    """Rasm so'rovlarini to'g'ri aniqlashni tekshiradi."""
    assert is_photo_requested("rasm tashla") is True
    assert is_photo_requested("qayerdasan?") is True
    assert is_photo_requested("nima qilyapsan, foto bormi") is True
    assert is_photo_requested("salom yaxshimisiz") is False
    assert is_photo_requested("bugun havo qanday?") is False


def test_get_photo_category():
    """Toifani kontekstga ko'ra to'g'ri tanlashni tekshiradi."""
    assert get_photo_category("qahvaxonadaman kofe ichyapman") == "coffee"
    assert get_photo_category("ishdaman noutbukda") == "work"
    assert get_photo_category("kitob o'qiyapman") == "study"
    assert get_photo_category("kechki shahar") == "evening"
    assert get_photo_category("uyda choy ichib") == "tea_home"


def test_get_photo_caption():
    """Har xil darajalar uchun mos caption qaytarilishini tekshiradi."""
    cap1 = get_photo_caption("coffee", level=1, role="qiz_dost", game_mode="story")
    assert "qahva" in cap1.lower() or "kofe" in cap1.lower()
    assert "jonim" not in cap1.lower()

    cap4 = get_photo_caption("coffee", level=4, role="qiz_dost", game_mode="story")
    assert "jonim" in cap4.lower() or "yonimda" in cap4.lower()

    cap_classic = get_photo_caption("coffee", level=1, role="qiz_dost", game_mode="classic")
    assert "sevgilim" in cap_classic.lower() or "sog'indim" in cap_classic.lower()
