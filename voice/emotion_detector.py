"""Qadirdon AI — Speech Emotion & Prosody Detector.

Xabar mazmuni, emojilar va intonatsiyani tahlil qilib, unga mos
emotsional rejim (romantik, quvnoq, tasalli, hayrat, sokin) va
audio parametrlarini (tezlik, pitch, ekvalayzer, undovlar) aniqlaydi.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class EmotionConfig:
    name: str
    speed: float           # VoiceLab va umumiy TTS tezligi (0.90 … 1.15)
    pitch_factor: float    # FFmpeg orqali tovush balandligi omili (0.96 … 1.04)
    lowpass_freq: int      # Hz
    eq_freq: int           # Hz (vokal mavjudligi yoki ko'krak iliqligi)
    eq_gain: float         # dB
    starter_interjections: tuple[str, ...]
    description: str


EMOTION_CONFIGS: dict[str, EmotionConfig] = {
    # 1. Romantik / Mehrli / Sog'inch (o'ta mayin, erkalovchi va xotirjam)
    "romantic": EmotionConfig(
        name="romantic",
        speed=0.80,
        pitch_factor=0.97,
        lowpass_freq=7200,
        eq_freq=350,
        eq_gain=2.5,
        starter_interjections=("Hmm... ", "Jonim... ", "Bilasanmi... ", "Sizga bitta gap aytaymi... "),
        description="Mayin, sokin, erkalovchi va yaqin ohang",
    ),
    # 2. Quvnoq / Sho'x / Hazilkash (xushchaqchaq, lekin shoshilmaydi)
    "joyful": EmotionConfig(
        name="joyful",
        speed=0.89,
        pitch_factor=1.02,
        lowpass_freq=7900,
        eq_freq=3000,
        eq_gain=2.8,
        starter_interjections=("Haha... ", "Voy... ", "Zo'r-ku... ", "Ajoyib... "),
        description="Quvnoq, o'ynoqi, xushchaqchaq ohang",
    ),
    # 3. Tasalli / Hamdardlik / G'amxo'rlik (bosiq, sekin, muloyim)
    "comforting": EmotionConfig(
        name="comforting",
        speed=0.82,
        pitch_factor=0.98,
        lowpass_freq=7300,
        eq_freq=400,
        eq_gain=2.2,
        starter_interjections=("Eh... ", "Xafa bo'lma-ya... ", "Xavotir olmang... ", "Hmm... "),
        description="Mehrli, dalda beruvchi va iliq ohang",
    ),
    # 4. Hayrat / Hayajon / Kutilmagan hodisa (qiziqish bilan, lekin tushunarli)
    "surprised": EmotionConfig(
        name="surprised",
        speed=0.87,
        pitch_factor=1.02,
        lowpass_freq=7800,
        eq_freq=2800,
        eq_gain=2.4,
        starter_interjections=("Voy... ", "Iya... ", "Nahotki... ", "Rostdanmi... "),
        description="Hayratlangan, qiziqqan ohang",
    ),
    # 5. Sokin / Vazmin / Kundalik suhbat (tabiiy, me'yordagi xotirjam tezlik)
    "calm": EmotionConfig(
        name="calm",
        speed=0.84,
        pitch_factor=1.00,
        lowpass_freq=7700,
        eq_freq=2800,
        eq_gain=2.0,
        starter_interjections=("Hmm... ", "Ha-ya... ", "Xa... "),
        description="Tabiiy, muvozanatli va xotirjam so'zlashuv",
    ),
}

# Emotsiyalarni aniqlash qoliplari
EMOTION_KEYWORDS: dict[str, list[str]] = {
    "romantic": [
        r"\bjonim\b", r"\bsevgilim\b", r"\byagonam\b", r"\byuragim\b",
        r"\bsog['’`‘]?indim\b", r"\bsevaman\b", r"\basalim\b", r"\bshirinim\b",
        r"\bshirin tushlar\b", r"\byaxshi dam oling\b", r"\bbag['’`‘]?rim\b",
        r"\bquchoqlayman\b", r"\byoningizdaman\b", r"\byoningdaman\b",
        r"\bjonajonim\b", r"\bmehrim\b",
    ],
    "joyful": [
        r"\bhaha\b", r"\bxaxa\b", r"\bzo['’`‘]?r\b", r"\bajoyib\b",
        r"\bquvnoq\b", r"\bhazil\b", r"\bqoyil\b", r"\byutdik\b",
        r"\bkulgi\b", r"\bmushuk\b", r"\bvoyvoy\b", r"\bkayfiyat\b",
        r"\bmazza\b", r"\buraa\b", r"\bofarin\b",
    ],
    "comforting": [
        r"\bxafa bo['’`‘]?lmang?\b", r"\bxavotir olma\b", r"\bsiqilmang?\b",
        r"\bcharchad", r"\bog['’`‘]?rima", r"\bhamma narsa yaxshi bo['’`‘]?ladi\b",
        r"\btinchlan", r"\bdam oling\b", r"\bqiynal", r"\byig['’`‘]?lama",
    ],
    "surprised": [
        r"\bvoy\b", r"\bnahotki\b", r"\brostdanmi\b", r"\biye\b",
        r"\bvoy-bo['’`‘]?\b", r"\bqanaqasiga\b", r"\bhaqiqatdanmi\b",
        r"\bhech qachon\b", r"\bshunaqami\b",
    ],
}

EMOTION_EMOJIS: dict[str, list[str]] = {
    "romantic": ["❤️", "🥰", "💕", "💖", "😘", "🌹", "🌸", "💌", "💋"],
    "joyful": ["😂", "🤣", "😄", "😁", "🥳", "🎉", "✨", "🔥", "😜", "😻"],
    "comforting": ["🥺", "🫂", "😔", "😢", "🙏", "💔", "🩹"],
    "surprised": ["😱", "😲", "😮", "👀", "⚡", "⁉️"],
}


def detect_speech_emotion(text: str) -> EmotionConfig:
    """Matn mazmuni va his-tuyg'ularini tahlil qilib, mos ovoz sozlamasini qaytaradi."""
    if not text:
        return EMOTION_CONFIGS["calm"]

    text_lower = text.lower()
    scores = {"romantic": 0, "joyful": 0, "comforting": 0, "surprised": 0}

    # 1. Emojilar bo'yicha baholash (har bir emoji 3 ball)
    for em, emojis in EMOTION_EMOJIS.items():
        for emoji in emojis:
            if emoji in text:
                scores[em] += 3

    # 2. Kalit so'zlar bo'yicha baholash (har bir so'z 2 ball)
    for em, patterns in EMOTION_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                scores[em] += 2

    # 3. Tinish belgilari ta'siri
    if text.count("!") >= 2:
        scores["joyful"] += 1
        scores["surprised"] += 1
    if "?!" in text or "!?" in text:
        scores["surprised"] += 2

    best_em = max(scores, key=scores.get)
    if scores[best_em] > 0:
        return EMOTION_CONFIGS[best_em]

    return EMOTION_CONFIGS["calm"]
