"""Qadirdon AI — Speech Humanizer (Matn fonetikasi, normalizatsiya va pauzalar muhandisligi).

TTS dvigatellari (VoiceLab, ElevenLabs, OpenAI va Edge-TTS) quruq kitobiy matnni emas,
balki jonli o'zbek so'zlashuv fonetikasini, nafas olish pauzalarini va
hissiy tovushlarni (interjections) tabiiy talaffuz qilishi uchun maxsus modul.
"""

from __future__ import annotations

import random
import re

from voice.emotion_detector import EmotionConfig, detect_speech_emotion
from voice.speech_normalizer import normalize_uzbek_text_for_speech

# Jonli o'zbek so'zlashuv fonetikasi (so'zlashuv qisqartmalari va talaffuz uyg'unlashuvi)
PHONETIC_REPLACEMENTS = [
    # 1. Inkor va fe'llar
    (r"\bbo['’`‘]?lmaydi\b", "bo'midi"),
    (r"\bbo['’`‘]?lmaydimi\b", "bo'midimi"),
    (r"\bbo['’`‘]?lmayapti\b", "bo'mayapti"),
    (r"\bbo['’`‘]?ladimi\b\?", "bo'ladimi...?"),
    (r"\bbo['’`‘]?laveradi\b", "bo'loradi"),
    (r"\bqilmayapti\b", "qimayapti"),
    (r"\bkelmayapti\b", "kemayapti"),
    (r"\bbormayapti\b", "bomayapti"),
    (r"\bbilmayman\b", "bilmiman"),
    (r"\bbilmaysizmi\b", "bilmisizmi"),
    (r"\bbilmaysanmi\b", "bilmisanmi"),
    (r"\bko['’`‘]?rmaysizmi\b", "ko'rmisizmi"),
    (r"\bko['’`‘]?rmaysanmi\b", "ko'rmisanmi"),
    (r"\bko['’`‘]?rmayapsanmi\b", "ko'rmayapsanmi-a"),
    (r"\baytmayman\b", "aytmiman"),

    # 2. O'tgan zamon davomiy shakllari
    (r"\bketayotgan edim\b", "ketvotuvdim"),
    (r"\bkelayotgan edim\b", "kelvotuvdim"),
    (r"\bqilayotgan edim\b", "qilvotuvdim"),
    (r"\bborayotgan edim\b", "borvotuvdim"),
    (r"\byozayotgan edim\b", "yozvotuvdim"),
    (r"\bishlayotgan edim\b", "ishlavotuvdim"),
    (r"\bgaplashayotgan edim\b", "gaplashvotuvdim"),
    (r"\bo['’`‘]?tirgan edim\b", "o'tiruvdim"),
    (r"\byotgan edim\b", "yotuvdim"),
    (r"\baytgan edim\b", "aytgandim"),
    (r"\bko['’`‘]?rgan edim\b", "ko'rgandim"),
    (r"\bbilgan edim\b", "bilgandim"),
    (r"\bbergan edim\b", "bergandim"),
    (r"\bolgan edim\b", "olgandim"),

    # 3. Hozirgi zamon talaffuzi
    (r"\bkelyapti\b", "kelyapdi"),
    (r"\bboryapti\b", "boryapdi"),
    (r"\bqilyapti\b", "qilyapdi"),

    # 4. So'roq va ta'kid shakllari
    (r"\baytgancha\b", "aytgancha-ya"),
    (r"\bemasmi\b\?", "emasmi-a?"),
    (r"\brostmi\b\?", "rostmi-a?"),
    (r"\bshunaqami\b\?", "shunaqami-a?"),
    (r"\bto['’`‘]?g['’`‘]?rimi\b\?", "to'g'rimi-a?"),
    (r"\bnima qilay\b", "nima qili"),
    (r"\bqanday qilib\b", "qande qilib"),

    # 5. Muloyim so'zlashuv qisqartmalari
    (r"\bovqatlandingizmi\b", "ovqatlandizmi"),
    (r"\bcharchadingizmi\b", "charchadizmi"),
    (r"\btushundingizmi\b", "tushundizmi"),
    (r"\buxladingizmi\b", "uxladizmi"),
    (r"\bkeldingizmi\b", "keldizmi"),
    (r"\bketdingizmi\b", "ketdizmi"),
    (r"\byetib\s+oldingizmi\b", "yetib oldizmi"),
    (r"\bbordingizmi\b", "bordizmi"),
    (r"\bko['’`‘]?rdingizmi\b", "ko'rdizmi"),
    (r"\baytdingizmi\b", "aytdizmi"),
    (r"\btuzukmisiz\b", "tuzumisiz"),
    (r"\byaxshimisiz\b", "yaxshisizmi"),
]

# Mavjud boshlang'ich salomlashish yoki tovushlar
EXISTING_STARTERS = (
    "salom", "assalomu", "voy", "ha", "xa", "hmm", "iye", "e-e",
    "yo'g'e", "xo'p", "rahmat", "raxmat", "bilasanmi", "bilasizmi",
    "ey", "o'zi", "qalay", "haha", "xaxa", "eh",
)

FEMALE_ROLES = {"qiz_dost", "ayol", "singil", "ona", "opa"}
MALE_ROLES = {"aka", "uka"}


def clean_text_for_speech(text: str) -> str:
    """Ovozga aylantirishdan oldin matnni to'liq normalizatsiya qiladi va tozalaydi."""
    if not text:
        return ""

    # Avval sonlar, qisqartmalar, apostrof va grammatikani normalizatsiya qilamiz
    normalized = normalize_uzbek_text_for_speech(text)

    # Emojilarni tozalash (TTS chalkashmasligi uchun)
    emoji_pattern = re.compile(
        r"[\U00010000-\U0010ffff]|[\u2000-\u32ff]|[\ud83c-\ud83e][\ud000-\udfff]",
        flags=re.UNICODE,
    )
    cleaned = emoji_pattern.sub("", normalized)

    # Bo'shliqlarni me'yorga keltirish
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def phonetic_tune_for_uzbek(text: str) -> str:
    """Kitobiy o'zbek so'zlarini jonli og'zaki so'zlashuv fonetikasiga o'tkazadi."""
    for pattern, repl in PHONETIC_REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


def insert_breath_and_pauses(
    text: str,
    emotion_name: str = "calm",
    pause_duration: float = 1.0,
) -> str:
    """Gaplar orasiga va bog'lovchilar oldiga tabiiy nafas olish pauzalarini (...) joylashtiradi."""
    pause_symbol = "... "

    # Gaplar orasidagi nuqtadan keyin mayin nafas to'xtashi
    text = re.sub(r"\.\s+", f"{pause_symbol}", text)

    # Bog'lovchilar oldidan nafas olish pauzasi (agar oldida tinish belgisi bo'lmasa)
    conjunctions = ["lekin", "chunki", "ammo", "biroq", "faqat", "agar"]
    for conj in conjunctions:
        text = re.sub(rf"(?<![.,?!…])\s+\b{conj}\b", f"... {conj}", text, flags=re.IGNORECASE)

    # Mehrli murojaat so'zlari oxiriga mayin to'xtash qo'shish
    affection_words = ["jonim", "sevgilim", "qadrdonim", "do'stim", "singlim", "ukaginam", "shirinim"]
    for aff in affection_words:
        text = re.sub(rf"\b{aff}\b(?=[.,!]|$)", f"{aff}...", text, flags=re.IGNORECASE)

    # Romantik yoki tasalli beruvchi rejimda gap oxiriga mayin nafas to'xtashi
    if emotion_name in {"romantic", "comforting"} and text and text[-1] in ".":
        text = text[:-1] + "..."

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
    probability: float = 0.40,
    emotion_config: EmotionConfig | None = None,
) -> str:
    """Gap boshiga his-tuyg'uga mos tovushlar (Haha..., Voy..., Jonim..., Hmm...) qo'shadi."""
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

    # Agar aniqlangan emotsiya konfiguratsiyasi bo'lsa, undan foydalanamiz
    if emotion_config and emotion_config.starter_interjections:
        filler = random.choice(emotion_config.starter_interjections)
        return filler + text

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
    emotion_config: EmotionConfig | None = None,
) -> str:
    """Matnni TTS ovozga aylantirishdan oldin emotsiyaga mos jonli va tabiiy holatga keltiradi."""
    if not text:
        return "Salom"

    if emotion_config is None:
        emotion_config = detect_speech_emotion(text, role=role)

    # 1. Tozalash va normalizatsiya (markdown, sonlar, qisqartmalar, apostroflar, grammatika)
    cleaned = clean_text_for_speech(text)
    if not cleaned:
        return "Salom"

    # 2. Fonetik o'zbekcha so'zlashuvga o'tkazish
    phonetic = phonetic_tune_for_uzbek(cleaned)

    # 3. Nafas olish va intonatsiya pauzalarini kiritish
    with_pauses = insert_breath_and_pauses(
        phonetic,
        emotion_name=emotion_config.name,
        pause_duration=getattr(emotion_config, "pause_duration", 1.0),
    )

    # 4. Hissiy undov tovushlarini joylashtirish
    humanized = inject_speech_interjections(
        with_pauses,
        role=role,
        level=level,
        emotion_config=emotion_config,
    )

    return humanized
