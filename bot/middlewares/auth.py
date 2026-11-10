"""Qadirdon AI — Autentifikatsiya middleware.

Har bir handler ishga tushishdan oldin foydalanuvchini bazadan tekshiradi
va `user` ob'ektini handler data'siga qo'shadi.
Tezkor ishlash uchun 30 soniyalik in-memory keshdan foydalanadi.
"""

from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.models import User
from db.session import async_session

_USER_CACHE: dict[int, tuple[float, User]] = {}
_USER_CACHE_TTL = 30.0  # 30 soniya


def invalidate_user_cache(telegram_id: int | None = None) -> None:
    """Foydalanuvchi ma'lumotlari yangilanganda keshni tozalash."""
    if telegram_id is not None:
        _USER_CACHE.pop(telegram_id, None)
    else:
        _USER_CACHE.clear()


class AuthMiddleware(BaseMiddleware):
    """Foydalanuvchini bazadan oladi yoki yaratadi va handler data'ga inject qiladi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Telegram foydalanuvchi ma'lumotlarini olish
        user_tg = None
        if isinstance(event, Message) and event.from_user:
            user_tg = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_tg = event.from_user

        if user_tg is None:
            return await handler(event, data)

        # 1. Tezkor in-memory keshni tekshirish
        now = time.monotonic()
        cached = _USER_CACHE.get(user_tg.id)
        if cached and (now - cached[0] < _USER_CACHE_TTL):
            data["user"] = cached[1]
            return await handler(event, data)

        # 2. Bazadan foydalanuvchini qidirish va bitta joined query bilan yuklash
        async with async_session() as session:
            stmt = (
                select(User)
                .where(User.telegram_id == user_tg.id)
                .options(
                    joinedload(User.subscription),
                    joinedload(User.ai_profiles),
                )
            )
            result = await session.execute(stmt)
            user = result.unique().scalar_one_or_none()

            if user is None:
                user = User(
                    telegram_id=user_tg.id,
                    username=user_tg.username,
                    full_name=user_tg.full_name or "",
                    language="uz",
                )
                session.add(user)
                await session.commit()
                # Yangilangan obyektni olish
                res = await session.execute(stmt)
                user = res.unique().scalar_one_or_none()

            if user is not None:
                _USER_CACHE[user_tg.id] = (now, user)

            data["user"] = user
            data["session"] = session

            return await handler(event, data)
