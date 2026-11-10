"""Qadirdon AI — Inson-ga o'xshash javob kechikishlari.

Xabar uzunligi, yozish tezligi va kun vaqtiga qarab
tabiiy kechikish hisoblaydi.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone


# Typing speed → belgilar/sekundda
_SPEED_CPS: dict[int, float] = {
    1: 30.0,   # sekin
    2: 60.0,   # normal
    3: 110.0,  # tez
}

# Kun vaqti bo'yicha multiplikator (soat → koeffitsiyent)
_TIME_MULTIPLIERS: dict[range, float] = {
    range(0, 6):   1.3,   # Tun
    range(6, 8):   1.1,   # Tong
    range(8, 20):  1.0,   # Kunduzi
    range(20, 24): 1.1,   # Kechqurun
}


def _get_time_multiplier(hour: int) -> float:
    """Berilgan soat uchun tezlik multiplikatorini qaytaradi."""
    for hour_range, multiplier in _TIME_MULTIPLIERS.items():
        if hour in hour_range:
            return multiplier
    return 1.0


def calculate_delay(
    text_length: int,
    typing_speed: int = 2,
    time_of_day: datetime | None = None,
) -> float:
    """Tabiiy javob kechikishini (sekundlarda) hisoblaydi.

    Parameters
    ----------
    text_length:
        Javob matning uzunligi (belgilar soni).
    typing_speed:
        1 = sekin, 2 = normal, 3 = tez.
    time_of_day:
        Hozirgi vaqt. ``None`` bo'lsa UTC ishlatiladi.

    Returns
    -------
    float
        Kechikish sekundlarda (jitter bilan).
    """
    if time_of_day is None:
        time_of_day = datetime.now(timezone.utc)

    cps = _SPEED_CPS.get(typing_speed, _SPEED_CPS[2])

    # Asosiy typing vaqti
    base_delay = text_length / cps

    # Kun vaqti multiplikatori
    multiplier = _get_time_multiplier(time_of_day.hour)
    base_delay *= multiplier

    # ±10% tasodifiy jitter
    jitter = base_delay * random.uniform(-0.10, 0.10)
    delay = base_delay + jitter

    # Tezlikka qarab maksimal cheklov
    max_limit = 0.8 if typing_speed == 3 else (1.8 if typing_speed == 2 else 3.0)
    delay = max(0.2, min(delay, max_limit))

    return round(delay, 2)
