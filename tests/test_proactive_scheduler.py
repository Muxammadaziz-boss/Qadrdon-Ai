"""Unit tests for Proactive Auto-Initiative and Scheduler."""

from datetime import datetime, timezone, timedelta
import pytest
from unittest.mock import AsyncMock, MagicMock

from business.tasks.proactive_scheduler import (
    get_current_slot,
    generate_proactive_text,
    check_and_run_proactive_messages,
    SLOTS,
)
from db.models import AiProfile


def test_get_current_slot():
    """Vaqt slotlari to'g'ri hisoblanishini tekshiradi."""
    tz = timezone(timedelta(hours=5))

    # Ertalab 08:30 -> morning
    dt_morning = datetime(2026, 11, 12, 8, 30, tzinfo=tz)
    assert get_current_slot(dt_morning) == "morning"

    # Tushlik 13:15 -> lunch
    dt_lunch = datetime(2026, 11, 12, 13, 15, tzinfo=tz)
    assert get_current_slot(dt_lunch) == "lunch"

    # Kechki 20:00 -> evening
    dt_evening = datetime(2026, 11, 12, 20, 0, tzinfo=tz)
    assert get_current_slot(dt_evening) == "evening"

    # Tun 03:00 -> None
    dt_night = datetime(2026, 11, 12, 3, 0, tzinfo=tz)
    assert get_current_slot(dt_night) is None


def test_generate_proactive_text():
    """Har xil rollar uchun proactive xabarlar muvaffaqiyatli generatsiya qilinishini tekshiradi."""
    import asyncio
    from unittest.mock import patch

    profile = AiProfile(
        role="qiz_dost",
        ai_name="Malika",
        relationship_level=1,
        game_mode="story",
        proactive_enabled=True,
    )
    with patch("business.tasks.proactive_scheduler.ai_engine.client", None):
        text = asyncio.run(generate_proactive_text(profile, slot="morning"))
        assert isinstance(text, str)
        assert len(text) > 5

        # Aka roli
        profile_aka = AiProfile(
            role="aka",
            ai_name="Sardor",
            relationship_level=2,
            proactive_enabled=True,
        )
        text_aka = asyncio.run(generate_proactive_text(profile_aka, slot="evening"))
        assert isinstance(text_aka, str)
        assert len(text_aka) > 5
