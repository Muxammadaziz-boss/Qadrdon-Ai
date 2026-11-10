"""Qadirdon AI — Uzoq muddatli xotira.

Ma'lumotlar bazasidan suhbat kontekstini va xulosa (summary)ni olish.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.conversation import Conversation
from db.models.message import Message


async def get_conversation_history(
    session: AsyncSession, conversation_id: int, limit: int = 15
) -> list[dict]:
    """Bazadan oxirgi xabarlarni yuklab beradi."""
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.id.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()

    # Xronologik tartibga keltirish
    messages = list(reversed(messages))
    return [{"role": m.role, "content": m.content} for m in messages]


async def update_conversation_summary(
    session: AsyncSession, conversation_id: int, summary: str
) -> None:
    """Suhbat haqidagi qisqacha xulosani yangilash."""
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await session.execute(stmt)
    conv = result.scalar_one_or_none()
    if conv:
        conv.last_context_summary = summary
        await session.commit()
