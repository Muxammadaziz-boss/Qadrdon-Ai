"""Qadirdon AI — Qisqa muddatli xotira (Redis / Tezkor xotira keshi).

Oxirgi suhbat xabarlarini tezkor o'qish uchun saqlaydi.
Redis mavjud bo'lmasa, avtomatik ravishda tezkor xotira (in-memory) keshiga o'tadi.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict
from loguru import logger
import redis.asyncio as aioredis
from config.settings import settings

redis_client: aioredis.Redis | None = None
_redis_available: bool = True
_last_redis_check: float = 0.0

# Redis mavjud bo'lmaganda tezkor xotirada saqlash uchun
_memory_cache: dict[int, list[dict]] = defaultdict(list)
_MAX_HISTORY_LEN = 20


async def get_redis() -> aioredis.Redis | None:
    """Redis mijozini olish. Agar ulanish imkoni bo'lmasa, None qaytaradi."""
    global redis_client, _redis_available, _last_redis_check

    now = time.monotonic()
    # Agar Redis ishlamagan bo'lsa, har 60 sekundda bir martagina qayta urinish
    if not _redis_available and (now - _last_redis_check < 60.0):
        return None

    if redis_client is None:
        try:
            redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=0.2,
                socket_timeout=0.2,
            )
        except Exception:
            _redis_available = False
            _last_redis_check = now
            return None

    return redis_client


async def save_recent_message(
    conversation_id: int, role: str, content: str
) -> None:
    """Xabarni keshga saqlash (Redis mavjud bo'lsa Redis, aks holda tezkor xotira)."""
    global _redis_available, _last_redis_check

    # Har doim tezkor xotiraga yozamiz (eng tezkor javob uchun)
    mem_list = _memory_cache[conversation_id]
    mem_list.append({"role": role, "content": content})
    if len(mem_list) > _MAX_HISTORY_LEN:
        _memory_cache[conversation_id] = mem_list[-_MAX_HISTORY_LEN:]

    r = await get_redis()
    if r is None:
        return

    try:
        key = f"conv:{conversation_id}:recent"
        payload = json.dumps({"role": role, "content": content})
        await r.rpush(key, payload)
        await r.ltrim(key, -_MAX_HISTORY_LEN, -1)
        await r.expire(key, 86400)
    except Exception as e:
        if _redis_available:
            logger.info("Redis ulanishi mavjud emas, tezkor in-memory kesh ishlatilmoqda.")
        _redis_available = False
        _last_redis_check = time.monotonic()


async def get_recent_messages(conversation_id: int) -> list[dict]:
    """Keshdan oxirgi suhbat xabarlarini olish."""
    global _redis_available, _last_redis_check

    # Agar tezkor xotirada bo'lsa, darhol qaytaramiz (0 ms)
    if conversation_id in _memory_cache and _memory_cache[conversation_id]:
        return list(_memory_cache[conversation_id])

    r = await get_redis()
    if r is None:
        return []

    try:
        key = f"conv:{conversation_id}:recent"
        items = await r.lrange(key, 0, -1)
        res = [json.loads(item) for item in items]
        if res:
            _memory_cache[conversation_id] = list(res)
        return res
    except Exception as e:
        _redis_available = False
        _last_redis_check = time.monotonic()
        return list(_memory_cache.get(conversation_id, []))

