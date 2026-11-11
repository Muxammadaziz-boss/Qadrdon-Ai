"""Qadirdon AI — Typing simulyatori.

Foydalanuvchiga tabiiy ko'rinish berish uchun "typing..." amalini
yuboradi va xabar uzunligiga qarab kutadi.
"""

from __future__ import annotations

import asyncio

from aiogram import Bot
from aiogram.enums import ChatAction
from loguru import logger


# O'rtacha belgilar/sekundda (typing_speed ga qarab)
_SPEED_MAP: dict[int, float] = {
    1: 30.0,   # sekin
    2: 65.0,   # normal
    3: 120.0,  # tez
}

# Minimal va maksimal typing davomiyligi (sekundlarda)
_MIN_TYPING_SECONDS = 0.3
_MAX_TYPING_SECONDS = 2.5

# Telegram «typing» statusi har 5 sekundda yangilanishi kerak
_TYPING_ACTION_INTERVAL = 4.5


async def simulate_typing(
    bot: Bot,
    chat_id: int,
    business_connection_id: str,
    text: str,
    typing_speed: int = 2,
) -> None:
    """Matn uzunligiga mos realistik «typing...» effektini ko'rsatadi.

    Parameters
    ----------
    bot:
        aiogram Bot instansiyasi.
    chat_id:
        Xabar yuboriladigan chat ID.
    business_connection_id:
        Business connection identifikatori (shaxsiy profil uchun).
    text:
        Yuboriladigan matn — uzunligi davomiylikni belgilaydi.
    typing_speed:
        1 = sekin, 2 = normal, 3 = tez.
    """
    chars_per_second = _SPEED_MAP.get(typing_speed, _SPEED_MAP[2])
    duration = len(text) / chars_per_second
    duration = max(_MIN_TYPING_SECONDS, min(duration, _MAX_TYPING_SECONDS))

    logger.debug(
        "Typing simulyatsiya: {} belgi, {:.1f}s (speed={})",
        len(text),
        duration,
        typing_speed,
    )

    elapsed = 0.0
    while elapsed < duration:
        try:
            await bot.send_chat_action(
                chat_id=chat_id,
                action=ChatAction.TYPING,
                business_connection_id=business_connection_id,
            )
        except Exception as exc:
            logger.warning("Typing action xatosi: {}", exc)
            break

        sleep_time = min(_TYPING_ACTION_INTERVAL, duration - elapsed)
        await asyncio.sleep(sleep_time)
        elapsed += sleep_time


async def simulate_recording_voice(
    bot: Bot,
    chat_id: int,
    business_connection_id: str,
    duration: float = 2.0,
) -> None:
    """Telegramda «ovozli xabar yozmoqda...» (record_voice) holatini ko'rsatadi."""
    try:
        await bot.send_chat_action(
            chat_id=chat_id,
            action=ChatAction.RECORD_VOICE,
            business_connection_id=business_connection_id,
        )
        await asyncio.sleep(duration)
    except Exception as exc:
        logger.warning("Record voice action xatosi: {}", exc)

