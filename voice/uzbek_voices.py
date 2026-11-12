"""Qadirdon AI — O'zbek Milliy Ovozlar Katalogi.

O'zbekiston milliy tabiiy ovozlari (VoiceLab.uz), yuqori hissiyotli inson ovozlari (ElevenLabs)
va zaxira Microsoft Edge-TTS profillarini yagona tizimda birlashtiruvchi katalog.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UzbekVoice:
    key: str
    name: str              # Masalan: "🌸 Lola — Tabiiy va jonli (Tavsiya)"
    gender: str            # "female" | "male" | "child"
    provider: str          # "voicelab" | "elevenlabs" | "edge"
    voice_id: str          # Masalan: "voice_EvIb9vE6iY_dWgK7OobYdZcX"
    edge_voice: str        # Fallback: "uz-UZ-MadinaNeural" yoki "uz-UZ-SardorNeural"
    edge_pitch: float      # Pitch sozlamasi
    edge_rate: float       # Tezlik sozlamasi
    description: str       # Qisqa ta'rif
    sample_phrase: str     # Eshitib ko'rish iborasi


# ── Barcha yangi O'zbek milliy ovozlari ─────────────────────────────────────────
UZBEK_VOICES: dict[str, UzbekVoice] = {
    # ── Ayollar va Qizlar ovozlari ──
    "lola": UzbekVoice(
        key="lola",
        name="🌸 Lola — Tabiiy va jonli (Tavsiya)",
        gender="female",
        provider="voicelab",
        voice_id="voice_EvIb9vE6iY_dWgK7OobYdZcX",
        edge_voice="uz-UZ-MadinaNeural",
        edge_pitch=0.0,
        edge_rate=0.96,
        description="Sho'x, samimiy va jonli o'zbek qiz ovozi",
        sample_phrase="Salom! Men Lola bo'laman, siz bilan suhbatlashishdan judayam xursandman 🌸",
    ),
    "madina": UzbekVoice(
        key="madina",
        name="🍯 Madina — Muloyim va mayin",
        gender="female",
        provider="voicelab",
        voice_id="voice_4ef06e6b-2229-4023-ad66-c2a7a2b736ff",
        edge_voice="uz-UZ-MadinaNeural",
        edge_pitch=1.5,
        edge_rate=0.92,
        description="Asaldek shirin, muloyim va sokin qiz ovozi",
        sample_phrase="Assalomu alaykum! Men Madinaman, ovozim sizga yoqdimi? Har doim yoningizdaman.",
    ),
    "nozima": UzbekVoice(
        key="nozima",
        name="🧕 Nozima — Sokin va bosiq",
        gender="female",
        provider="voicelab",
        voice_id="voice_3602ec76-5393-43b6-9e0d-784328cb77ba",
        edge_voice="uz-UZ-MadinaNeural",
        edge_pitch=-1.0,
        edge_rate=0.90,
        description="Vazmin, sokin va mayin ayol ovozi",
        sample_phrase="Salom. Kuningiz xayrli va tinch o'tsin, men Nozima bo'laman.",
    ),
    "kamola": UzbekVoice(
        key="kamola",
        name="✨ Kamola — Ipakdek nafis",
        gender="female",
        provider="voicelab",
        voice_id="voice_47260d60-5635-4fb0-904d-0f3c19c04ce6",
        edge_voice="uz-UZ-MadinaNeural",
        edge_pitch=2.0,
        edge_rate=0.92,
        description="Ipakdek mayin, yoqimli va shivirlashga yaqin ovoz",
        sample_phrase="Salom azizim! Men Kamolaman, ovozim sizga yoqadi degan umiddaman.",
    ),
    "safiya": UzbekVoice(
        key="safiya",
        name="🕊 Safiya — Vazmin suhbatdosh",
        gender="female",
        provider="voicelab",
        voice_id="voice_2785aabd-21b5-4cc7-9845-2230186ef7d9",
        edge_voice="uz-UZ-MadinaNeural",
        edge_pitch=-0.5,
        edge_rate=0.94,
        description="Maslahatchi, samimiy va bosiq suhbatdosh",
        sample_phrase="Assalomu alaykum. Xush kelibsiz, keling barchasini xotirjam gaplashib olamiz.",
    ),
    "dilnoza": UzbekVoice(
        key="dilnoza",
        name="🌹 Dilnoza — Baxmal ovoz",
        gender="female",
        provider="voicelab",
        voice_id="voice_f7179d1c-07ab-4b3d-b5be-84dcf2935388",
        edge_voice="uz-UZ-MadinaNeural",
        edge_pitch=0.5,
        edge_rate=0.95,
        description="Mayin va chuqur baxmal ayol ovozi",
        sample_phrase="Salom! Men Dilnozaman, bugungi rejalaringiz qanday?",
    ),

    # ── Erkaklar ovozlari ──
    "davron": UzbekVoice(
        key="davron",
        name="👨 Davronbek — Samimiy va iliq (Tavsiya)",
        gender="male",
        provider="elevenlabs",
        voice_id="agoC45V78njTIxYzwmSb",
        edge_voice="uz-UZ-SardorNeural",
        edge_pitch=0.0,
        edge_rate=0.96,
        description="Jonli, o'ta samimiy va iliq inson ovozi",
        sample_phrase="Salom do'stim! Men Davronbekman, ishlaring yaxshimi? Har doim aloqadaman 🤝",
    ),
    "amir": UzbekVoice(
        key="amir",
        name="📖 Amir — Hikoyanavis va vazmin",
        gender="male",
        provider="voicelab",
        voice_id="voice_8bae02c6-d078-4757-9d62-0fce6da23cf7",
        edge_voice="uz-UZ-SardorNeural",
        edge_pitch=-2.0,
        edge_rate=0.92,
        description="Chuqur, iliq va hikoya qiluvchi mulohazali ovoz",
        sample_phrase="Assalomu alaykum. Men Amir bo'laman, keling bugun qiziqarli mavzularda suhbatlashamiz.",
    ),
    "sardor": UzbekVoice(
        key="sardor",
        name="⚡ Sardor — Qat'iyatli yigit",
        gender="male",
        provider="voicelab",
        voice_id="voice_xdQMoRJkjHbPIB-jounXzKq8",
        edge_voice="uz-UZ-SardorNeural",
        edge_pitch=1.0,
        edge_rate=1.02,
        description="Qat'iyatli, baquvvat yigit ovozi",
        sample_phrase="Salom! Men Sardorman, barcha maqsadlaringizga birga erishamiz!",
    ),
    "jasur": UzbekVoice(
        key="jasur",
        name="🎙 Jasur — Salobatli va chuqur",
        gender="male",
        provider="voicelab",
        voice_id="voice_ba303813-3023-48aa-a454-4b5705669d35",
        edge_voice="uz-UZ-SardorNeural",
        edge_pitch=-3.5,
        edge_rate=0.90,
        description="Salobatli, chuqur va xotirjam erkak ovozi",
        sample_phrase="Salom. Barchasi yaxshi, xotirjam ishlarimizni davom ettiramiz.",
    ),
    "javohir": UzbekVoice(
        key="javohir",
        name="🌟 Javohir — Yorqin notiq",
        gender="male",
        provider="voicelab",
        voice_id="voice_fa56cecf-9b0b-45ba-9ec3-494efb5b301f",
        edge_voice="uz-UZ-SardorNeural",
        edge_pitch=1.5,
        edge_rate=1.04,
        description="Yorqin, baquvvat va chaqqon notiq ovozi",
        sample_phrase="Assalomu alaykum! Men Javohirman, yangi marralar sari birga harakat qilamiz!",
    ),
    "abdulhay": UzbekVoice(
        key="abdulhay",
        name="🦸‍♂️ Abdulhay — Qahramon ovozi",
        gender="male",
        provider="voicelab",
        voice_id="voice_M-p5iz9z_kPWNm_C0cFqbC6X",
        edge_voice="uz-UZ-SardorNeural",
        edge_pitch=2.0,
        edge_rate=1.05,
        description="Piter Parker dublyaj ovozi, jonli va o'ynoqi",
        sample_phrase="Salom! Men Abdulhayman, bugun ajoyib kun bo'ladi, ishonchim komil!",
    ),
    "child_playful": UzbekVoice(
        key="child_playful",
        name="🧒 Kenjatoy — Quvnoq bola",
        gender="child",
        provider="voicelab",
        voice_id="voice_83a39d68-22bc-4062-b86e-0a9dd998ba7a",
        edge_voice="uz-UZ-MadinaNeural",
        edge_pitch=6.0,
        edge_rate=1.12,
        description="Quvnoq, chaqqon va sho'x kenjatoy ovozi",
        sample_phrase="Salom! Keling, birga o'ynaymiz va qiziq narsalar haqida gaplashamiz! 😄",
    ),
}

# Eski umumiy kalitlarni yangi aniq milliy ovozlarga o'giruvchi xarita
VOICE_KEY_ALIASES: dict[str, str] = {
    # Ayollar
    "female_soft": "madina",
    "female_warm": "lola",
    "female_bright": "lola",
    "female_calm": "nozima",
    # Erkaklar
    "male_warm": "davron",
    "male_deep": "jasur",
    "male_calm": "amir",
    "male_energetic": "sardor",
}

FEMALE_VOICE_KEYS: list[str] = ["lola", "madina", "nozima", "kamola", "safiya", "dilnoza"]
MALE_VOICE_KEYS: list[str] = ["davron", "amir", "sardor", "jasur", "javohir", "abdulhay"]


def resolve_voice_key(key: str | None) -> str:
    """Har qanday kalitni (eski yoki yangi) kanonik kalitga o'tkazadi."""
    if not key:
        return "lola"
    return VOICE_KEY_ALIASES.get(key, key)


def get_uzbek_voice(key: str | None) -> UzbekVoice:
    """Kanonik ovoz obyektini qaytaradi (topilmasa Lola)."""
    canonical = resolve_voice_key(key)
    return UZBEK_VOICES.get(canonical, UZBEK_VOICES["lola"])
