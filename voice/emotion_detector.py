"""Qadirdon AI — Speech Emotion & Prosody Detector.

Xabar mazmuni, emojilar va intonatsiyani tahlil qilib, unga mos
emotsional rejim (romantik, quvnoq, tasalli, hayrat, sho'x, jiddiy, sokin) va
audio parametrlarini (tezlik, pitch, ekvalayzer, undovlar, fonetik shiddat) aniqlaydi.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import re


@dataclass(frozen=True, slots=True)
class EmotionConfig:
    name: str
    speed: float           # VoiceLab va umumiy TTS tezligi (0.75 … 0.95)
    pitch_factor: float    # FFmpeg orqali tovush balandligi omili (0.96 … 1.04)
    lowpass_freq: int      # Hz
    eq_freq: int           # Hz (vokal mavjudligi yoki ko'krak iliqligi)
    eq_gain: float         # dB
    starter_interjections: tuple[str, ...]
    description: str
    intensity: float = 1.0          # Emotsiya shiddati (0.5 ... 1.5)
    phonetic_intensity: float = 1.0 # Fonetik o'zgarishlar darajasi (0.0 ... 1.0)
    pause_duration: float = 1.0     # Nafas va pauzalar ko'paytiruvchisi


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
        intensity=1.1,
        phonetic_intensity=1.0,
        pause_duration=1.2,
    ),
    # 2. Quvnoq / Sho'x / Xursandchilik (xushchaqchaq, lekin shoshilmaydi)
    "joyful": EmotionConfig(
        name="joyful",
        speed=0.88,
        pitch_factor=1.02,
        lowpass_freq=7900,
        eq_freq=3000,
        eq_gain=2.8,
        starter_interjections=("Haha... ", "Voy... ", "Zo'r-ku... ", "Ajoyib... "),
        description="Quvnoq, o'ynoqi, xushchaqchaq ohang",
        intensity=1.2,
        phonetic_intensity=1.0,
        pause_duration=0.9,
    ),
    # 3. Tasalli / Hamdardlik / G'amxo'rlik (bosiq, sekin, muloyim)
    "comforting": EmotionConfig(
        name="comforting",
        speed=0.81,
        pitch_factor=0.98,
        lowpass_freq=7300,
        eq_freq=400,
        eq_gain=2.2,
        starter_interjections=("Eh... ", "Xafa bo'lma-ya... ", "Xavotir olmang... ", "Hmm... "),
        description="Mehrli, dalda beruvchi va iliq ohang",
        intensity=1.0,
        phonetic_intensity=0.9,
        pause_duration=1.25,
    ),
    # 4. Hayrat / Hayajon / Kutilmagan hodisa (qiziqish bilan, lekin tushunarli)
    "surprised": EmotionConfig(
        name="surprised",
        speed=0.86,
        pitch_factor=1.03,
        lowpass_freq=7800,
        eq_freq=2800,
        eq_gain=2.4,
        starter_interjections=("Voy... ", "Iye... ", "Nahotki... ", "Rostdanmi... "),
        description="Hayratlangan, qiziqqan ohang",
        intensity=1.15,
        phonetic_intensity=1.0,
        pause_duration=0.95,
    ),
    # 5. Sho'x / Nozli / Erka (hazilkash, sho'x qiz/yigit)
    "playful": EmotionConfig(
        name="playful",
        speed=0.85,
        pitch_factor=1.02,
        lowpass_freq=7600,
        eq_freq=2600,
        eq_gain=2.5,
        starter_interjections=("Voy qarang-a... ", "Iye-iye... ", "E-e... ", "Arazlayman hozir... "),
        description="Sho'x, noz-karashmali va hazilkash ohang",
        intensity=1.1,
        phonetic_intensity=1.0,
        pause_duration=1.0,
    ),
    # 6. O'ychan / Jiddiy / Vazmin (chuqur o'y, maslahat, jiddiylik)
    "serious": EmotionConfig(
        name="serious",
        speed=0.81,
        pitch_factor=0.98,
        lowpass_freq=7400,
        eq_freq=320,
        eq_gain=2.0,
        starter_interjections=("O'ylab qoldim... ", "Bilasanmi nima... ", "To'g'risi... ", "Hmm... "),
        description="O'ychan, jiddiy va vazmin ohang",
        intensity=0.9,
        phonetic_intensity=0.7,
        pause_duration=1.15,
    ),
    # 7. Sokin / Vazmin / Kundalik suhbat (tabiiy, me'yordagi xotirjam tezlik)
    "calm": EmotionConfig(
        name="calm",
        speed=0.84,
        pitch_factor=1.00,
        lowpass_freq=7700,
        eq_freq=2800,
        eq_gain=2.0,
        starter_interjections=("Hmm... ", "Ha-ya... ", "Xa... "),
        description="Tabiiy, muvozanatli va xotirjam so'zlashuv",
        intensity=1.0,
        phonetic_intensity=0.85,
        pause_duration=1.0,
    ),
}

# Emotsiyalarni aniqlash qoliplari
EMOTION_KEYWORDS: dict[str, list[str]] = {
    "romantic": [
        r"\bjonim\b", r"\bsevgilim\b", r"\byagonam\b", r"\byuragim\b",
        r"\bsog['’`‘]?indim\b", r"\bsevaman\b", r"\basalim\b", r"\bshirinim\b",
        r"\bshirin tushlar\b", r"\byaxshi dam oling\b", r"\bbag['’`‘]?rim\b",
        r"\bquchoqlayman\b", r"\byoningizdaman\b", r"\byoningdaman\b",
        r"\bjonajonim\b", r"\bmehrim\b", r"\berkam\b",
    ],
    "joyful": [
        r"\bhaha\b", r"\bxaxa\b", r"\bzo['’`‘]?r\b", r"\bajoyib\b",
        r"\bquvnoq\b", r"\bqoyil\b", r"\byutdik\b",
        r"\bkulgi\b", r"\bmushuk\b", r"\bvoyvoy\b", r"\bkayfiyat\b",
        r"\bmazza\b", r"\buraa\b", r"\bofarin\b", r"\byashang\b",
    ],
    "comforting": [
        r"\bxafa bo['’`‘]?lmang?\b", r"\bxavotir olma\b", r"\bsiqilmang?\b",
        r"\bcharchad", r"\bog['’`‘]?rima", r"\bhamma narsa yaxshi bo['’`‘]?ladi\b",
        r"\btinchlan", r"\bdam oling\b", r"\bqiynal", r"\byig['’`‘]?lama",
        r"\bdardingiz\b", r"\bhammasi o['’`‘]?tib ketadi\b",
    ],
    "surprised": [
        r"\bvoy\b", r"\bnahotki\b", r"\brostdanmi\b", r"\biye\b",
        r"\bvoy-bo['’`‘]?\b", r"\bqanaqasiga\b", r"\bhaqiqatdanmi\b",
        r"\bhech qachon\b", r"\bshunaqami\b", r"\bdahshat\b",
    ],
    "playful": [
        r"\baraz\b", r"\bhazil\b", r"\btentak\b", r"\bjinni\b",
        r"\bsho['’`‘]?x\b", r"\bqaysar\b", r"\baldamang\b", r"\bo['’`‘]?ynoqi\b",
        r"\berkal", r"\bkulma\b", r"\bko['’`‘]?rasiz hali\b",
    ],
    "serious": [
        r"\bmuhim\b", r"\bjiddiy\b", r"\bmasala\b", r"\bqaror\b",
        r"\bo['’`‘]?ylayapman\b", r"\bkelajak\b", r"\bishonch\b", r"\bhayot\b",
        r"\bmaslahat\b", r"\bto['’`‘]?g['’`‘]?ri tushun\b",
    ],
}

EMOTION_EMOJIS: dict[str, list[str]] = {
    "romantic": ["❤️", "🥰", "💕", "💖", "😘", "🌹", "🌸", "💌", "💋", "💐"],
    "joyful": ["😂", "🤣", "😄", "😁", "🥳", "🎉", "✨", "🔥", "😻", "🎊"],
    "comforting": ["🥺", "🫂", "😔", "😢", "🙏", "💔", "🩹", "🥀"],
    "surprised": ["😱", "😲", "😮", "👀", "⚡", "⁉️", "🤯"],
    "playful": ["😜", "😝", "🤪", "😏", "🤭", "😋", "🙈"],
    "serious": ["🤔", "🧐", "😐", "📝", "⚖️", "⏳"],
}


def detect_speech_emotion(
    text: str,
    role: str | None = None,
    emotion_override: str | None = None,
    speed_override: float | None = None,
    pitch_override: float | None = None,
    intensity: float = 1.0,
) -> EmotionConfig:
    """Matn mazmuni va his-tuyg'ularini tahlil qilib, mos ovoz sozlamasini qaytaradi.
    
    Qo'llab-quvvatlanadigan parametrlar:
    - emotion_override: foydalanuvchi yoki tizim belgilagan aniq emotsiya nomi
    - speed_override: nutq sur'atini bevosita sozlash (masalan 0.82)
    - pitch_override: ovoz balandligini sozlash
    - intensity: emotsiya intensivligi koeffitsienti
    """
    if emotion_override and emotion_override in EMOTION_CONFIGS:
        base_cfg = EMOTION_CONFIGS[emotion_override]
        new_speed = speed_override if speed_override is not None else base_cfg.speed
        new_pitch = pitch_override if pitch_override is not None else base_cfg.pitch_factor
        return replace(base_cfg, speed=new_speed, pitch_factor=new_pitch, intensity=intensity)

    if not text:
        base_cfg = EMOTION_CONFIGS["calm"]
        return base_cfg

    scores: dict[str, float] = {
        "romantic": 0.0,
        "joyful": 0.0,
        "comforting": 0.0,
        "surprised": 0.0,
        "playful": 0.0,
        "serious": 0.0,
        "calm": 0.1,  # Baza ehtimollik
    }

    # Rol bo'yicha tabiiy moyillik (role bias)
    if role in {"qiz_dost", "ayol"}:
        scores["romantic"] += 0.3
        scores["playful"] += 0.2
    elif role in {"ona", "opa"}:
        scores["comforting"] += 0.4
    elif role in {"aka", "uka"}:
        scores["joyful"] += 0.2

    # 1. Emojilarni tekshirish (kuchli signal)
    for emotion, emojis in EMOTION_EMOJIS.items():
        for emoji in emojis:
            if emoji in text:
                scores[emotion] += 2.0

    # 2. Kalit so'zlar va iboralarni tekshirish
    lower_text = text.lower()
    for emotion, patterns in EMOTION_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, lower_text):
                scores[emotion] += 1.5

    # 3. Tinish belgilariga qarab intonatsiya baholash
    if lower_text.count("!") >= 2 or "?!" in lower_text:
        scores["surprised"] += 1.2
        scores["joyful"] += 0.8

    if "..." in text and scores["romantic"] > 0:
        scores["romantic"] += 0.8

    # Eng yuqori ball to'plagan emotsiyani tanlash
    best_emotion = max(scores.items(), key=lambda x: x[1])[0]

    # Agar hech qanday emotsiya yetarli ball olmasa — sokin (calm)
    if scores[best_emotion] < 0.8:
        best_emotion = "calm"

    base_cfg = EMOTION_CONFIGS.get(best_emotion, EMOTION_CONFIGS["calm"])

    # Maxsus parametrlar berilgan bo'lsa, ularni qo'llash
    final_speed = speed_override if speed_override is not None else base_cfg.speed
    final_pitch = pitch_override if pitch_override is not None else base_cfg.pitch_factor

    return replace(
        base_cfg,
        speed=final_speed,
        pitch_factor=final_pitch,
        intensity=intensity,
    )
