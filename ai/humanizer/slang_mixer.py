"""Qadirdon AI — Slang Mixer.

O'zbekcha Telegram chatlariga xos qisqartmalar va so'zlashuv iboralari.
"""

import random
import re

SLANG_DICTIONARY = {
    "rahmat": ["raxmat", "katta raxmat", "tashakkur"],
    "mayli": ["mayli", "mayli xo'p", "xo'p"],
    "xo'p": ["xp", "xop", "xo'p bo'ladi"],
    "nima": ["nma", "nima gap"],
    "qanday": ["qanaqa", "qandey"],
    "yaxshi": ["yaxwi", "zo'r", "joyida"],
    "qayerda": ["qatta", "qayerdasiz"],
    "qachon": ["qachonroq", "qachon"],
    "iltimos": ["iltimos", "plz"],
    "ha": ["haa", "xa", "albatta"],
    "yo'q": ["yoq", "yo'g'e", "yo"],
    "hozir": ["xozir", "hozirroq", "xoz"],
}

_WORD_REGEX = re.compile(r"^(\W*)(.*?)(\W*)$", re.UNICODE)


def fix_conversational_grammar(text: str) -> str:
    """Sun'iy kitobiy yoki eshitilgan zamon shakllarini jonli o'zbekcha so'zlashuv shakliga o'tkazadi."""
    replacements = [
        (r"\bchiqibdimi\b", "chiqdimi"),
        (r"\bchiqibdimi\?", "chiqdimi?"),
        (r"\bbo'libdimi\b", "bo'ldimi"),
        (r"\bkelibdimi\b", "keldimi"),
        (r"\bko'ribsizmi\b", "ko'rdingizmi"),
        (r"\bqilibsizmi\b", "qildingizmi"),
        (r"\bcharchabsizmi\b", "charchadingizmi"),
        (r"\bovqatlanibsizmi\b", "ovqatlandingizmi"),
        (r"\byetib\s+olibsizmi\b", "yetib oldingizmi"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


def mix_slang(text: str, use_slang: bool = True) -> str:
    """Matndagi ba'zi so'zlarni Telegram chatiga xos jonli variantlarga almashtiradi."""
    if not use_slang:
        return text

    words = text.split()
    new_words = []

    for word in words:
        match = _WORD_REGEX.match(word)
        if not match:
            new_words.append(word)
            continue

        prefix, core, suffix = match.groups()
        clean_word = core.lower()

        if clean_word in SLANG_DICTIONARY and random.random() < 0.25:
            replacement = random.choice(SLANG_DICTIONARY[clean_word])
            if core and core[0].isupper():
                replacement = replacement.capitalize()
            new_words.append(f"{prefix}{replacement}{suffix}")
        else:
            new_words.append(word)

    return " ".join(new_words)
