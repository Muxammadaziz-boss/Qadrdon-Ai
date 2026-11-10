"""Qadirdon AI — Ovoz profillari.

Har bir ovoz turi uchun Google Cloud TTS parametrlarini
belgilaydi: ovoz nomi, tezlik, balandlik va ovoz balandligi.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True, slots=True)
class VoiceProfile:
    """Bitta ovoz profilining sozlamalari."""

    # Google TTS voice name (tilga qarab almashinadi)
    voice_name_uz: str
    voice_name_ru: str
    # SSML ovoz parametrlari
    pitch: float  # semitones (-20.0 … +20.0)
    speaking_rate: float  # 0.25 … 4.0
    volume_gain_db: float  # -96.0 … +16.0


# ---------------------------------------------------------------------------
# Mavjud ovoz profillari
# ---------------------------------------------------------------------------
# Google Cloud TTS hozirda o'zbek tilini to'liq qo'llab-quvvatlamaydi.
# Quyidagi "uz" voice nomlari eng yaqin muqobil sifatida ko'rsatilgan.
# Haqiqiy ishlatishda mavjud bo'lgan ovozlarni tekshiring:
#   https://cloud.google.com/text-to-speech/docs/voices
# ---------------------------------------------------------------------------

VOICE_PROFILES: Dict[str, VoiceProfile] = {
    # Iliq erkak ovozi — do'stona, samimiy ton
    "male_warm": VoiceProfile(
        voice_name_uz="uz-UZ-Standard-A",  # Mavjud bo'lmasa, tr-TR-Standard-A
        voice_name_ru="ru-RU-Standard-D",
        pitch=-1.0,
        speaking_rate=1.0,
        volume_gain_db=0.0,
    ),
    # Chuqur erkak ovozi — ishonchli, jiddiy ton
    "male_deep": VoiceProfile(
        voice_name_uz="uz-UZ-Standard-A",
        voice_name_ru="ru-RU-Standard-B",
        pitch=-4.0,
        speaking_rate=0.95,
        volume_gain_db=1.0,
    ),
    # Yumshoq ayol ovozi — tinch, xotirjam ton
    "female_soft": VoiceProfile(
        voice_name_uz="uz-UZ-Standard-A",
        voice_name_ru="ru-RU-Standard-A",
        pitch=2.0,
        speaking_rate=0.95,
        volume_gain_db=-1.0,
    ),
    # Iliq ayol ovozi — do'stona, jonli ton
    "female_warm": VoiceProfile(
        voice_name_uz="uz-UZ-Standard-A",
        voice_name_ru="ru-RU-Standard-C",
        pitch=1.0,
        speaking_rate=1.05,
        volume_gain_db=0.0,
    ),
    # Yorqin ayol ovozi — quvnoq, musiqiy ton
    "female_bright": VoiceProfile(
        voice_name_uz="uz-UZ-Standard-A",
        voice_name_ru="ru-RU-Standard-C",
        pitch=3.0,
        speaking_rate=1.1,
        volume_gain_db=1.0,
    ),
    # Vazmin ayol ovozi — bosiq, sokin ton
    "female_calm": VoiceProfile(
        voice_name_uz="uz-UZ-Standard-A",
        voice_name_ru="ru-RU-Standard-A",
        pitch=0.5,
        speaking_rate=0.92,
        volume_gain_db=0.0,
    ),
    # Vazmin erkak ovozi — mulohazali ton
    "male_calm": VoiceProfile(
        voice_name_uz="uz-UZ-Standard-A",
        voice_name_ru="ru-RU-Standard-D",
        pitch=-2.0,
        speaking_rate=0.92,
        volume_gain_db=0.0,
    ),
    # Qat'iyatli yigit ovozi — chaqqon, baquvvat ton
    "male_energetic": VoiceProfile(
        voice_name_uz="uz-UZ-Standard-A",
        voice_name_ru="ru-RU-Standard-B",
        pitch=0.0,
        speaking_rate=1.1,
        volume_gain_db=1.0,
    ),
    # Quvnoq bola ovozi — balandroq va tezroq ton
    "child_playful": VoiceProfile(
        voice_name_uz="uz-UZ-Standard-A",
        voice_name_ru="ru-RU-Standard-A",
        pitch=6.0,
        speaking_rate=1.15,
        volume_gain_db=1.5,
    ),
}

# Standart profil (agar ko'rsatilmagan bo'lsa)
DEFAULT_VOICE_TYPE = "female_warm"
