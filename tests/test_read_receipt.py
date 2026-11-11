"""Unit tests for mark_business_message_as_read helper."""

import asyncio
from unittest.mock import AsyncMock
import pytest
from business.utils.read_receipt import mark_business_message_as_read


def test_mark_business_message_as_read_success():
    """Bot.read_business_message muvaffaqiyatli chaqirilishini tekshiradi."""
    mock_bot = AsyncMock()
    mock_bot.read_business_message.return_value = True

    result = asyncio.run(
        mark_business_message_as_read(
            bot=mock_bot,
            business_connection_id="conn_123",
            chat_id=123456,
            message_id=789,
        )
    )
    assert result is True
    mock_bot.read_business_message.assert_awaited_once_with(
        business_connection_id="conn_123",
        chat_id=123456,
        message_id=789,
    )


def test_mark_business_message_as_read_missing_args():
    """Parametrlardan biri bo'sh bo'lsa False qaytarishini tekshiradi."""
    mock_bot = AsyncMock()
    result = asyncio.run(
        mark_business_message_as_read(
            bot=mock_bot,
            business_connection_id="",
            chat_id=123456,
            message_id=789,
        )
    )
    assert result is False


def test_mark_business_message_as_read_handles_exception():
    """Xatolik yuz berganda crash bo'lmasdan False qaytarishini tekshiradi."""
    mock_bot = AsyncMock()
    mock_bot.read_business_message.side_effect = RuntimeError("Telegram API timeout")

    result = asyncio.run(
        mark_business_message_as_read(
            bot=mock_bot,
            business_connection_id="conn_123",
            chat_id=123456,
            message_id=789,
        )
    )
    assert result is False
