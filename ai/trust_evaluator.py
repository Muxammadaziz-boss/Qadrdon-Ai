"""Qadirdon AI — Ishonch va Munosabat Baholovchisi (Trust / Affection XP Engine).

Foydalanuvchi xabarlarini tahlil qilib, ishonch ballarini (+XP / -XP) hisoblaydi
va daraja ko'tarilishi yoki tushishini aniqlaydi.
"""

from __future__ import annotations
import re
from typing import Any
from ai.prompts.relationship_levels import calculate_level_from_xp, get_level_info

# Ijobiy iboralar va signallar
POSITIVE_PATTERNS = [
    # Salomlashish va odob
    (r"\b(assalomu\s+alaykum|salom|hayrli\s+(tong|kun|kech)|qandaysiz|yaxshimisiz)\b", 4),
    (r"\b(rahmat|katta\s+rahmat|tashakkur|minnatdorman|salomat\s+bo'ling|baraka\s+toping)\b", 6),
    (r"\b(iltimos|marhamat|uzr|kechirasiz|kechiring|aybga\s+buyurmaysiz)\b", 5),
    # G'amxo'rlik va mehr
    (r"\b(ovqatland(ing|ingiz)mi|charchamad(ing|ingiz)mi|dam\s+ol(ing)?|issiq\s+kiyin(ing)?)\b", 12),
    (r"\b(tinchlikmi|sog'lig'(ing|ingiz)\s+yaxshimi|kayfiyat(ing|ingiz)\s+qalay)\b", 8),
    (r"\b(o'zing(iz)?ni\s+ehtiyot\s+qil(ing)?|xavotir\s+oldim|yaxshi\s+dam\s+ol(ing)?)\b", 10),
    # Kompliment va iliq so'zlar
    (r"\b(yaxshiyam\s+borsan|zo'rsan|aqllisan|chiroylisan|go'zalsan|shirinsan|yoqimlisan)\b", 10),
    (r"\b(kayfiyatimni\s+ko'tarding|sen\s+bilan\s+gaplashish\s+yoqimli|seni\s+tushunaman)\b", 12),
    (r"\b(jannatim|onajon|onajonim|duo\s+qiling|akaxon|opajon|singiljon|ukajon)\b", 8),
    (r"\b(yaxshi\s+ko'raman|sog'indim|qadrlayman|hurmat\s+qilaman)\b", 15),
]

# Salbiy va haqoratli so'zlar
NEGATIVE_PATTERNS = [
    (r"\b(jinni|ahmoq|tentak|ablax|iflos|dalbayob|mol|eshak|chmo|shumshuk)\b", -25),
    (r"\b(yo'qol|dafxo'r|yo'qol\s+ko'zimdan|yoqmayapsan|asabimga\s+tegma|o'chir\s+ovozingni)\b", -20),
    (r"\b(bema'ni|gapirma|tentakmisan|aqling\s+yo'qmi|yomon\s+xotin|yaramas)\b", -15),
    (r"\b(sanga\s+gapirib\s+bo'lmaydi|bezor\s+qilding|keraging\s+yo'q)\b", -18),
]


def evaluate_message_trust(
    user_text: str,
    current_xp: int,
    current_level: int,
    role: str,
    game_mode: str = "story",
) -> dict[str, Any]:
    """
    Foydalanuvchi xabarini tahlil qilib, yangi XP va darajani qaytaradi.
    Klassik rejimda XP hisoblash shart emas, har doim 5-darajada turadi.
    """
    if game_mode == "classic":
        return {
            "delta_xp": 0,
            "new_xp": 1000,
            "old_level": 5,
            "new_level": 5,
            "leveled_up": False,
            "leveled_down": False,
            "level_info": get_level_info(role, 5),
        }

    text_lower = (user_text or "").lower()
    delta_xp = 0

    # 1. Ijobiy signallarni tekshirish
    matched_positives = 0
    for pattern, points in POSITIVE_PATTERNS:
        if re.search(pattern, text_lower):
            delta_xp += points
            matched_positives += 1

    # 2. Salbiy signallarni tekshirish
    matched_negatives = 0
    for pattern, penalty in NEGATIVE_PATTERNS:
        if re.search(pattern, text_lower):
            delta_xp += penalty
            matched_negatives += 1

    # 3. Agar na ijobiy, na salbiy bo'lsa, oddiy xushmuomala suhbat uchun kichik XP (+2)
    if matched_positives == 0 and matched_negatives == 0:
        if len(text_lower.strip()) > 3:
            delta_xp = 2

    # 4. Chegaralarni hisoblash
    old_xp = current_xp
    new_xp = max(0, min(1200, old_xp + delta_xp))
    new_level = calculate_level_from_xp(new_xp)
    old_level = current_level

    leveled_up = new_level > old_level
    leveled_down = new_level < old_level

    return {
        "delta_xp": delta_xp,
        "new_xp": new_xp,
        "old_level": old_level,
        "new_level": new_level,
        "leveled_up": leveled_up,
        "leveled_down": leveled_down,
        "level_info": get_level_info(role, new_level),
    }
