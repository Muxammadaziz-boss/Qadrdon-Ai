"""Qadirdon AI — Speech Normalizer & Text Polisher.

Ovoz generatsiyasidan (TTS) va jonli muloqotdan oldin matnni to'liq normalizatsiya qilish:
1. Sonlarni o'zbekcha so'zlarga aylantirish (kardinal, tartib, vaqt, foiz, miqdor, valyuta).
2. Qisqartmalar va texnik atamalarni o'zbekcha talaffuzga moslash (AI -> Ey-Ay, SMS -> es-em-es).
3. Tutuq belgisi va apostroflarni standartlashtirish (’, ‘, ʻ, ʼ, ` -> ').
4. Jonli so'zlashuv grammatikasini to'g'rilash (chiqibdimi -> chiqdimi, qilibsizmi -> qildingizmi).
5. Markdown, emoji va tizim belgilarini tozalash.
"""

from __future__ import annotations

import re

# 1. Barcha noan'anaviy apostroflarni standart ' belgisiga keltirish
APOSTROPHE_PATTERN = re.compile(r"[`’‘ʼʻ´'\u02bb\u02bc\u2018\u2019]")

# 2. Qisqartmalar va chet tili atamalari fonetikasi
ABBREVIATION_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bAI\b", re.IGNORECASE), "Ey-Ay"),
    (re.compile(r"\bIT\b", re.IGNORECASE), "Ay-Ti"),
    (re.compile(r"\bSMS\b", re.IGNORECASE), "es-em-es"),
    (re.compile(r"\bOK\b", re.IGNORECASE), "oke"),
    (re.compile(r"\bOk\b"), "oke"),
    (re.compile(r"\bID\b", re.IGNORECASE), "ay-di"),
    (re.compile(r"\bAPI\b", re.IGNORECASE), "ey-pi-ay"),
    (re.compile(r"\bURL\b", re.IGNORECASE), "yu-ar-el"),
    (re.compile(r"\bTG\b", re.IGNORECASE), "Telegram"),
    (re.compile(r"\bGB\b", re.IGNORECASE), "gigabayt"),
    (re.compile(r"\bMB\b", re.IGNORECASE), "megabayt"),
    (re.compile(r"\bKB\b", re.IGNORECASE), "kilobayt"),
    (re.compile(r"\bkm\b", re.IGNORECASE), "kilometr"),
    (re.compile(r"\bkg\b", re.IGNORECASE), "kilogramm"),
    (re.compile(r"\bsm\b", re.IGNORECASE), "santimetr"),
    (re.compile(r"\bmin\b", re.IGNORECASE), "daqiqa"),
    (re.compile(r"\bsek\b", re.IGNORECASE), "soniya"),
]

# 3. Jonli so'zlashuv grammatikasi qoidalari (kitobiy / eshitilgan o'tgan zamon -> bevosita o'tgan zamon)
SPOKEN_GRAMMAR_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bchiqibdimi\b", re.IGNORECASE), "chiqdimi"),
    (re.compile(r"\bbo['’`‘]?libdimi\b", re.IGNORECASE), "bo'ldimi"),
    (re.compile(r"\bkelibdimi\b", re.IGNORECASE), "keldimi"),
    (re.compile(r"\bketibdimi\b", re.IGNORECASE), "ketdimi"),
    (re.compile(r"\bko['’`‘]?ribdimi\b", re.IGNORECASE), "ko'rdimi"),
    (re.compile(r"\byozibdimi\b", re.IGNORECASE), "yozdimi"),
    (re.compile(r"\bberibdimi\b", re.IGNORECASE), "berdimi"),
    (re.compile(r"\bolibdimi\b", re.IGNORECASE), "oldimi"),
    (re.compile(r"\bqilibdimi\b", re.IGNORECASE), "qildimi"),
    (re.compile(r"\btushunibdimi\b", re.IGNORECASE), "tushundimi"),
    (re.compile(r"\beshitibdimi\b", re.IGNORECASE), "eshitdimi"),
    (re.compile(r"\buxlab\s+qolibdimi\b", re.IGNORECASE), "uxlab qoldimi"),
    (re.compile(r"\baytibsizmi\b", re.IGNORECASE), "aytdingizmi"),
    (re.compile(r"\bkelibsizmi\b", re.IGNORECASE), "keldingizmi"),
    (re.compile(r"\bketibsizmi\b", re.IGNORECASE), "ketdingizmi"),
    (re.compile(r"\bqilibsizmi\b", re.IGNORECASE), "qildingizmi"),
    (re.compile(r"\bko['’`‘]?ribsizmi\b", re.IGNORECASE), "ko'rdingizmi"),
    (re.compile(r"\bcharchabsizmi\b", re.IGNORECASE), "charchadingizmi"),
    (re.compile(r"\bovqatlanibsizmi\b", re.IGNORECASE), "ovqatlandingizmi"),
    (re.compile(r"\bbilibsizmi\b", re.IGNORECASE), "bildingizmi"),
    (re.compile(r"\beshitibsizmi\b", re.IGNORECASE), "eshitdingizmi"),
    (re.compile(r"\btushunibsizmi\b", re.IGNORECASE), "tushundingizmi"),
    (re.compile(r"\byetib\s+olibsizmi\b", re.IGNORECASE), "yetib oldingizmi"),
    (re.compile(r"\buxlab\s+qolibsizmi\b", re.IGNORECASE), "uxlab qoldingizmi"),
    (re.compile(r"\bko['’`‘]?rdingizmi\b", re.IGNORECASE), "ko'rdingizmi"),
]

_ONES = ["", "bir", "ikki", "uch", "to'rt", "besh", "olti", "yetti", "sakkiz", "to'qqiz"]
_TENS = ["", "o'n", "yigirma", "o'ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to'qson"]


def int_to_uzbek(n: int) -> str:
    """Butun sonni o'zbek tilidagi so'z shakliga aylantiradi (0..999,999,999,999)."""
    if n == 0:
        return "nol"
    if n < 0:
        return "minus " + int_to_uzbek(abs(n))

    parts: list[str] = []

    if n >= 1_000_000_000:
        b = n // 1_000_000_000
        parts.append(int_to_uzbek(b) + " milliard")
        n %= 1_000_000_000

    if n >= 1_000_000:
        m = n // 1_000_000
        parts.append(int_to_uzbek(m) + " million")
        n %= 1_000_000

    if n >= 1000:
        k = n // 1000
        parts.append("ming" if k == 1 and not parts else int_to_uzbek(k) + " ming")
        n %= 1000

    if n >= 100:
        h = n // 100
        parts.append("yuz" if h == 1 else _ONES[h] + " yuz")
        n %= 100

    if n >= 10:
        t = n // 10
        parts.append(_TENS[t])
        n %= 10

    if n > 0:
        parts.append(_ONES[n])

    return " ".join(parts).strip()


def to_ordinal_uzbek(word: str) -> str:
    """So'z bilan ifodalangan sonni tartib son shakliga (-nchi / -inchi) aylantiradi."""
    word = word.strip()
    if not word:
        return word
    # Agar oxirgi harf unli bo'lsa: -nchi (masalan: ikki -> ikkinchi, yetti -> yettinchi)
    if word.endswith(("i", "a", "o", "u", "e")):
        return word + "nchi"
    return word + "inchi"


def unify_apostrophes(text: str) -> str:
    """Matndagi turli shakldagi apostroflarni yagona standart ' belgisiga keltiradi."""
    if not text:
        return ""
    # O'zbek harflari o' va g' uchun maxsus tekshiruv
    text = APOSTROPHE_PATTERN.sub("'", text)
    return text


def fix_spoken_grammar(text: str) -> str:
    """Jonli muloqotga mos bo'lmagan sun'iy zamon shakllarini to'g'rilaydi (katta/kichik harflarni saqlagan holda)."""
    for pattern, repl in SPOKEN_GRAMMAR_RULES:
        def _replacer(m: re.Match, replacement: str = repl) -> str:
            val = m.group(0)
            if val and val[0].isupper():
                return replacement[0].upper() + replacement[1:]
            return replacement
        text = pattern.sub(_replacer, text)
    return text


def normalize_abbreviations(text: str) -> str:
    """Texnik qisqartmalar va xalqaro so'zlarni tabiiy talaffuzga moslaydi."""
    for pattern, repl in ABBREVIATION_MAP:
        text = pattern.sub(repl, text)
    return text


def normalize_numbers(text: str) -> str:
    """Matndagi raqamlar, vaqtlar, foizlar va tartib sonlarni so'zga aylantiradi."""
    if not text:
        return ""

    # 1. Soat va vaqt (masalan: 14:30 -> o'n to'rt o'ttiz)
    def _replace_time(match: re.Match) -> str:
        h = int(match.group(1))
        m = int(match.group(2))
        h_str = int_to_uzbek(h)
        m_str = "nol nol" if m == 0 else int_to_uzbek(m)
        return f"{h_str} {m_str}"

    text = re.sub(r"\b(\d{1,2}):(\d{2})\b", _replace_time, text)

    # 2. Foizlar (masalan: 50% yoki %50 -> ellik foiz)
    def _replace_percent(match: re.Match) -> str:
        num = int(match.group(1))
        return f"{int_to_uzbek(num)} foiz"

    text = re.sub(r"\b(\d+)\s*%", _replace_percent, text)
    text = re.sub(r"%\s*(\d+)\b", _replace_percent, text)

    # 3. Yil va qo'shimchalar (masalan: 2026-yil, 2026-yilda, 2026 yilda)
    def _replace_year(match: re.Match) -> str:
        num = int(match.group(1))
        suffix = match.group(2)
        word = int_to_uzbek(num)
        return f"{to_ordinal_uzbek(word)} {suffix}"

    text = re.sub(r"\b(19\d{2}|20\d{2})[- ](yil(?:da|ga|dan|ning|i)?)\b", _replace_year, text)

    # 4. Tartib sonlar (masalan: 1-chi, 2-, 5-chi, 1-o'rin -> birinchi, ikkinchi, birinchi o'rin)
    def _replace_ordinal(match: re.Match) -> str:
        num = int(match.group(1))
        word = int_to_uzbek(num)
        return f"{to_ordinal_uzbek(word)} "

    text = re.sub(r"\b(\d+)(?:-chi|-inchi|-nchi|-)\s*", _replace_ordinal, text)

    # 5. Miqdor qo'shimchasi bilan (masalan: 5 ta -> beshta, 10 dona -> o'nta)
    def _replace_quantifier(match: re.Match) -> str:
        num = int(match.group(1))
        word = int_to_uzbek(num)
        return f"{word}ta"

    text = re.sub(r"\b(\d+)\s*(?:ta|dona)\b", _replace_quantifier, text)

    # 6. Valyuta (masalan: 5000 so'm, $100, 100$)
    def _replace_currency_dollar(match: re.Match) -> str:
        num = int(match.group(1))
        return f"{int_to_uzbek(num)} dollar"

    text = re.sub(r"\$\s*(\d+)\b", _replace_currency_dollar, text)
    text = re.sub(r"\b(\d+)\s*\$", _replace_currency_dollar, text)

    # 7. Qolgan oddiy sonlar (masalan: 5, 25, 1000)
    def _replace_plain_number(match: re.Match) -> str:
        num = int(match.group(1))
        return int_to_uzbek(num)

    text = re.sub(r"\b(\d+)\b", _replace_plain_number, text)

    return text


def clean_markdown_and_system_tags(text: str) -> str:
    """Markdown, URL va xabar meta-teglarini tozalaydi."""
    if not text:
        return ""

    # [Ovozli xabar: ...] kabi tizim teglarini tozalash
    text = re.sub(r"\[(?:Ovozli xabar|Ovozli javob|Rasm)[^\]]*\]", "", text, flags=re.IGNORECASE)

    # URL manzillarni tozalash
    text = re.sub(r"https?://\S+", "", text)

    # Markdown formatlash belgilarini tozalash (*kursiv*, **qalin**, `kod`, # sarlavha, > iqtibos)
    text = re.sub(r"[*_~`#>]", "", text)

    # Ko'p nuqta yoki ortiqcha tinish belgilarini me'yorga keltirish
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_uzbek_text_for_speech(text: str) -> str:
    """
    Ovoz sintezi (TTS) va tabiiy so'zlashuv uchun matnni to'liq normalizatsiya qiladi.
    Ketma-ketlik:
    1. Markdown va tizim belgilarini tozalash
    2. Apostroflarni unifikatsiya qilish
    3. Jonli so'zlashuv grammatikasini to'g'rilash (chiqibdimi -> chiqdimi)
    4. Qisqartmalarni kengaytirish (AI -> Ey-Ay)
    5. Sonlarni so'zga aylantirish (15:30 -> o'n besh o'ttiz, 5 ta -> beshta)
    """
    if not text:
        return ""

    # 1. Tozalash
    cleaned = clean_markdown_and_system_tags(text)

    # 2. Apostroflar
    unified = unify_apostrophes(cleaned)

    # 3. Grammatika
    grammared = fix_spoken_grammar(unified)

    # 4. Qisqartmalar
    abbreviated = normalize_abbreviations(grammared)

    # 5. Sonlar
    normalized = normalize_numbers(abbreviated)

    # Yakuniy tozalash
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized
