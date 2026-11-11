"""Qadirdon AI — Telegram Business xabarlarni o'qilgan (read receipt / double true) qilish.

Foydalanuvchi xabarlarini avtomatik tarzda o'qilgan (✓✓) holatiga o'tkazadi.
"""

from __future__ import annotations

from aiogram import Bot
from loguru import logger


async def mark_business_message_as_read(
    bot: Bot,
    business_connection_id: str,
    chat_id: int,
    message_id: int,
) -> bool:
    """Telegram Business xabarini o'qilgan (double checkmark / ✓✓) holatiga o'tkazadi.

    Parameters
    ----------
    bot:
        aiogram Bot instansiyasi.
    business_connection_id:
        Telegram Business ulanish identifikatori.
    chat_id:
        Suhbatdosh chat ID raqami.
    message_id:
        O'qilgan deb belgilanishi kerak bo'lgan xabar ID si.

    Returns
    -------
    bool:
        Muvaffaqiyatli o'qilgan bo'lsa True, aks holda False.
    """
    if not business_connection_id or not chat_id or not message_id:
        return False

    try:
        if hasattr(bot, "read_business_message"):
            result = await bot.read_business_message(
                business_connection_id=business_connection_id,
                chat_id=chat_id,
                message_id=message_id,
            )
            logger.debug(
                "Xabar o'qildi (✓✓ double true): connection={}, chat={}, msg_id={}, result={}",
                business_connection_id,
                chat_id,
                message_id,
                result,
            )
            return bool(result)
    except Exception as exc:
        logger.debug(
            "Xabarni o'qilgan qilishda xatolik (read_business_message): {}",
            exc,
        )
    return False
