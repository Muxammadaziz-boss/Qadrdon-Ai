"""Qadirdon AI — Emoji Inserter.

Rol va his-tuyg'uga mos emojilarni tabiiy joylashtirish.
"""

import random


def insert_emojis(text: str, emoji_level: int | None, role_emojis: list[str]) -> str:
    """Matn oxiriga yoki mos joyiga emoji qo'shadi."""
    level = emoji_level if emoji_level is not None else 2
    if level <= 0 or not role_emojis:
        return text

    chance = {1: 0.2, 2: 0.6, 3: 0.9}.get(level, 0.5)

    # Agar matnda allaqachon emoji bo'lsa yoki tasodifiy ehtimollik tushmasa
    if random.random() > chance:
        return text

    # Agar oxirida emoji bo'lmasa, bitta yoki ikkita mos emoji qo'shish
    chosen_emoji = random.choice(role_emojis)
    if emoji_level == 3 and random.random() < 0.5:
        chosen_emoji += random.choice(role_emojis)

    return f"{text.rstrip()} {chosen_emoji}"
