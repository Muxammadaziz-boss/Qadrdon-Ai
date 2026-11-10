"""Qadirdon AI — Kvestlar boshqaruvi va sirlarni ochish tizimi (Quest Engine).

Oddiy, Favqulodda va Yashirin kvestlarni qayta ishlaydi.
"""

from __future__ import annotations
import re
from typing import Any


def check_secret_quest_trigger(
    user_text: str,
    character: dict[str, Any] | None,
    unlocked_secrets: list[str] | None = None,
) -> dict[str, Any] | None:
    """Foydalanuvchi xabari personajning yashirin sirini ochganini tekshiradi."""
    if not character or "secret_trigger" not in character:
        return None

    secret = character["secret_trigger"]
    secret_id = f"{character.get('id')}_secret"

    if unlocked_secrets and secret_id in unlocked_secrets:
        return None  # Sir allaqachon ochilgan

    text_lower = (user_text or "").lower()
    keywords = secret.get("keywords", [])

    for kw in keywords:
        if kw.lower() in text_lower:
            return {
                "type": "secret",
                "id": secret_id,
                "title": secret["title"],
                "story": secret["story"],
                "reward_xp": secret.get("reward_xp", 80),
            }

    return None


def check_active_quest_completion(
    user_text: str,
    active_quest: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Hozir faol bo'lgan oddiy yoki favqulodda kvest bajarilganini tekshiradi."""
    if not active_quest or "pattern" not in active_quest:
        return None

    pattern = active_quest["pattern"]
    text_lower = (user_text or "").lower()

    if re.search(pattern, text_lower):
        return {
            "type": active_quest.get("type", "normal"),
            "id": active_quest.get("id"),
            "title": active_quest.get("title"),
            "reward_xp": active_quest.get("reward_xp", 20),
        }

    return None
