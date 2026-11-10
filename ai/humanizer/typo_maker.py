"""Qadirdon AI — Typo Maker.

Insondek tasodifiy imloviy xatolar qo'shish va ba'zan uni tuzatish.
"""

import random


def add_typos(text: str, probability: float = 0.05) -> tuple[str, str | None]:
    """
    Matnga tabiiy xato qo'shadi va ba'zan yulduzcha bilan tuzatish qaytaradi.
    Returns:
        (xatoli_matn, tuzatish_matni_yoki_None)
    """
    if len(text) < 5 or random.random() > probability:
        return text, None

    chars = list(text)
    # Tasodifiy bir so'z o'rtasidagi harfni tanlash
    candidates = [
        i for i, c in enumerate(chars) if c.isalpha() and 0 < i < len(chars) - 1
    ]
    if not candidates:
        return text, None

    idx = random.choice(candidates)
    typo_type = random.choice(["swap", "drop", "double"])

    original_word = _extract_word_at(text, idx)

    if typo_type == "swap" and idx < len(chars) - 1 and chars[idx + 1].isalpha():
        chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
    elif typo_type == "drop":
        chars.pop(idx)
    elif typo_type == "double":
        chars.insert(idx, chars[idx])

    corrupted_text = "".join(chars)

    # 40% ehtimollik bilan keyingi xabar sifatida tuzatish yuborish (*so'z)
    correction = None
    if original_word and random.random() < 0.4:
        correction = f"*{original_word}"

    return corrupted_text, correction


def _extract_word_at(text: str, idx: int) -> str | None:
    start = idx
    while start > 0 and text[start - 1].isalpha():
        start -= 1
    end = idx
    while end < len(text) and text[end].isalpha():
        end += 1
    word = text[start:end]
    return word if len(word) >= 3 else None
