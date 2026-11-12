"""Qadirdon AI — Speech Humanizer (Matn fonetikasi va pauzalar muhandisligi).

TTS dvigatellari (ElevenLabs va Edge-TTS) quruq kitobiy matnni emas,
balki jonli o'zbek so'zlashuv fonetikasini, nafas olish pauzalarini va
hissiy tovushlarni (interjections) tabiiy talaffuz qilishi uchun maxsus modul.
"""

from __future__ import annotations

import random
import re

# Jonli o'zbek so'zlashuv fonetikasi
PHONETIC_REPLACEMENTS = [
    # Inkor va zamon shakllari
    (r"\bbo['’`‘]?lmaydi\b", "bo'midi"),
    (r"\bbo['’`‘]?lmaydimi\b", "bo'midimi"),
    (r"\bbo['’`‘]?lmayapti\b", "bo'mayapti"),
    (r"\bbo['’`‘]?ladimi\b\?", "bo'ladimi...?"),
    (r"\bketayotgan edim\b", "ketvotuvdim"),
    (r"\bkelayotgan edim\b", "kelvotuvdim"),
    (r"\bqilayotgan edim\b", "qilvotuvdim"),
    (r"\bbilmayman\b", "bilmiman"),
    (r"\bbilmaysizmi\b", "bilmisizmi"),
    (r"\bnima qilay\b", "nima qili"),
    (r"\baytgancha\b", "aytgancha-ya"),
    (r"\bemasmi\b\?", "emasmi-a?"),
    (r"\bovqatlandingizmi\b", "ovqatlandizmi"),
    (r"\bcharchadingizmi\b", "charchadizmi"),
    (r"\bkelyapti\b", "kelyapdi"),
    (r"\bko['’`‘]?rmayapsanmi\b", "ko'rmayapsanmi-a"),
    (r"\byetib\s+oldingizmi\b", "yetib oldizmi"),
]

# Mavjud boshlang'ich salomlashish yoki tovushlar
EXISTING_STARTERS = (
    "salom", "assalomu", "voy", "ha", "xa", "hmm", "iye", "e-e",
    "yo'g'e", "xo'p", "rahmat", "raxmat", "bilasanmi", "bilasizmi",
    "ey", "o'zi", "qalay",
)

FEMALE_ROLES = {"qiz_dost", "ayol", "singil", "ona", "opa"}
MALE_ROLES = {"aka", "uka"}


def clean_text_for_speech(text: str) -> str:
    """Ovozga aylantirishdan oldin matnni markdown, URL va emojilardan tozalaydi."""
    if not text:
        return ""

    # Markdown belgilarini tozalash (*kursiv*, **qalin**, `kod`, # sarlavha, > iqtibos)
    cleaned = re.sub(r"[*_~`#>]", "", text)
    # URL manzillarni tozalash
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    # Emojilarni tozalash
    emoji_pattern = re.compile(
        r"[\U00010000-\U0010ffff]|[\u2000-\u32ff]|[\ud83c-\ud83e][\ud000-\udfff]",
        flags=re.UNICODE,
    )
    cleaned = emoji_pattern.sub("", cleaned)
    # Bo'shliqlarni me'yorga keltirish
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def phonetic_tune_for_uzbek(text: str) -> str:
    """Kitobiy o'zbek so'zlarini jonli og'zaki so'zlashuv fonetikasiga o'tkazadi."""
    for pattern, repl in PHONETIC_REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


def insert_breath_and_pauses(text: str) -> str:
    """Gaplar orasiga va bog'lovchilar oldiga tabiiy nafas olish pauzalarini (...) joylashtiradi."""
    # Bog'lovchilar oldidan nafas olish pauzasi (agar oldida tinish belgisi bo'lmasa)
    conjunctions = ["lekin", "chunki", "ammo", "biroq", "faqat"]
    for conj in conjunctions:
        text = re.sub(rf"(?<![.,?!…])\s+\b{conj}\b", f"... {conj}", text, flags=re.IGNORECASE)

    # Mehrli murojaat so'zlari oxiriga mayin to'xtash qo'shish
    affection_words = ["jonim", "sevgilim", "qadrdonim", "do'stim", "singlim", "ukaginam"]
    for aff in affection_words:
        text = re.sub(rf"\b{aff}\b(?=[.,!]|$)", f"{aff}...", text, flags=re.IGNORECASE)

    # Tinish belgilaridagi ortiqcha takrorlanishlarni tozalash (masalan: ...? -> ?)
    text = re.sub(r"\.{2,}([?!])", r"\1", text)
    text = re.sub(r"([?!])\.{2,}", r"\1", text)
    text = re.sub(r"\.{4,}", "...", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def inject_speech_interjections(
    text: str,
    role: str = "qiz_dost",
    level: int = 1,
    probability: float = 0.35,
) -> str:
    """Gap boshiga hissiy tovushlar (Hmm..., Voy..., Xa...) qo'shadi."""
    if not text:
        return text

    words = text.split()
    if not words:
        return text

    first_word = words[0].lower().strip(".,?!\"'")
    if any(first_word.startswith(st) for st in EXISTING_STARTERS):
        return text

    if random.random() > probability:
        return text

    if role in FEMALE_ROLES:
        if "?" in text:
            filler = random.choice(["Hmm... ", "Ha-ya... ", "Voy... "])
        else:
            filler = random.choice(["Hmm... ", "Bilasanmi... ", "Ha aytgancha... "])
    elif role in MALE_ROLES:
        if "?" in text:
            filler = random.choice(["Xa... ", "Hmm... "])
        else:
            filler = random.choice(["Xa... ", "Hmm... ", "Bilasanmi... ", "Qara... "])
    else:
        filler = "Hmm... "

    return filler + text


def humanize_for_speech(
    text: str,
    role: str = "qiz_dost",
    level: int = 1,
) -> str:
    """Matnni TTS ovozga aylantirishdan oldin insondek jonli va tabiiy holatga keltiradi."""
    if not text:
        return "Salom"

    # 1. Tozalash (markdown, emoji, URL)
    cleaned = clean_text_for_speech(text)
    if not cleaned:
        return "Salom"

    # 2. Fonetik o'zbekcha so'zlashuvga o'tkazish
    phonetic = phonetic_tune_for_uzbek(cleaned)

    # 3. Nafas olish va intonatsiya pauzalarini kiritish
    with_pauses = insert_breath_and_pauses(phonetic)

    # 4. Hissiy undov tovushlarini joylashtirish
    humanized = inject_speech_interjections(with_pauses, role=role, level=level)

    return humanized
