"""Qadirdon AI — Yordamchi funksiyalar."""

from datetime import datetime, timezone
import re


def escape_markdown(text: str) -> str:
    """Telegram MarkdownV2 belgilarni escape qiladi."""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Matnni ko'rsatilgan uzunlikda qisqartiradi."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_time_ago(dt: datetime) -> str:
    """Vaqt oralig'ini o'zbek tilida chiroyli ko'rsatadi."""
    now = datetime.now(timezone.utc)
    diff = (now - dt).total_seconds()

    if diff < 60:
        return "hozirgina"
    elif diff < 3600:
        minutes = int(diff // 60)
        return f"{minutes} daqiqa oldin"
    elif diff < 86400:
        hours = int(diff // 3600)
        return f"{hours} soat oldin"
    else:
        days = int(diff // 86400)
        return f"{days} kun oldin"


def is_valid_name(name: str) -> bool:
    """AI ismi to'g'ri kiritilganini tekshiradi."""
    name = name.strip()
    if len(name) < 2 or len(name) > 30:
        return False
    # Maxsus taqiqlangan belgilar yo'qligini tekshirish
    return bool(re.match(r"^[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳ\s'-]+$", name))
