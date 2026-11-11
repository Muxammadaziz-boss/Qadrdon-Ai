"""Unit tests for Relationship Diary and Dossier."""

from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock

from bot.handlers.diary import diary_keyboard, back_to_diary_keyboard, render_diary_content
from db.models import AiProfile, User


def test_diary_keyboards():
    """Kundalik klaviaturalari to'g'ri shakllanishini tekshiradi."""
    kb = diary_keyboard()
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "diary:secrets" in callbacks
    assert "diary:facts" in callbacks
    assert "settings:relationship" in callbacks
    assert "diary:show" in callbacks

    back_kb = back_to_diary_keyboard()
    assert back_kb.inline_keyboard[0][0].callback_data == "diary:show"


def test_render_diary_content_no_profile():
    """Profil mavjud bo'lmaganda ogohlantirish qaytarilishini tekshiradi."""
    import asyncio
    user = User(id=999, telegram_id=999888, username="testuser")
    text, kb = asyncio.run(render_diary_content(user))
    assert "Profil topilmadi" in text
