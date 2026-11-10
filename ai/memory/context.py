"""Qadirdon AI — Kontekst yig'uvchi modul."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from ai.memory.short_term import get_recent_messages, save_recent_message
from ai.memory.long_term import get_conversation_history


async def build_context(
    session: AsyncSession, conversation_id: int
) -> list[dict]:
    """
    Suhbat xotirasini birlashtiradi:
    1. Avval Redisdan tekshiradi.
    2. Redisda bo'lmasa, SQL bazadan olib Redisga to'ldiradi.
    """
    history = await get_recent_messages(conversation_id)
    if not history:
        history = await get_conversation_history(session, conversation_id)
        for msg in history:
            await save_recent_message(
                conversation_id, msg["role"], msg["content"]
            )

    return history
