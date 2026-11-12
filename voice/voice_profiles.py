"""Qadirdon AI — Ovoz profillari.

Har bir ovoz turi uchun TTS parametrlarini belgilaydi:
ovoz nomi, tezlik, balandlik va ovoz kuchi.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True, slots=True)
class VoiceProfile:
    """Bitta ovoz profilining sozlamalari."""

    voice_name_uz: str
    voice_name_ru: str
    pitch: float          # semitones / Hz sozlamasi
    speaking_rate: float  # tezlik nisbati (0.5 … 2.0)
    volume_gain_db: float


# ---------------------------------------------------------------------------
# Mavjud ovoz profillari (Microsoft Edge Neural / Google TTS)
# ---------------------------------------------------------------------------
VOICE_PROFILES: Dict[str, VoiceProfile] = {
    # Iliq erkak ovozi — do'stona, samimiy ton
    "male_warm": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=0.0,
        speaking_rate=1.0,
        volume_gain_db=0.0,
    ),
    # Chuqur erkak ovozi — ishonchli, jiddiy ton
    "male_deep": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=-4.0,
        speaking_rate=0.94,
        volume_gain_db=1.0,
    ),
    # Yumshoq ayol ovozi — tinch, xotirjam ton
    "female_soft": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=2.0,
        speaking_rate=0.95,
        volume_gain_db=-1.0,
    ),
    # Iliq ayol ovozi — do'stona, jonli ton
    "female_warm": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=0.0,
        speaking_rate=1.0,
        volume_gain_db=0.0,
    ),
    # Yorqin ayol ovozi — quvnoq, musiqiy ton
    "female_bright": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=4.0,
        speaking_rate=1.08,
        volume_gain_db=1.0,
    ),
    # Vazmin ayol ovozi — bosiq, sokin ton
    "female_calm": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=-1.0,
        speaking_rate=0.92,
        volume_gain_db=0.0,
    ),
    # Vazmin erkak ovozi — mulohazali ton
    "male_calm": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=-2.0,
        speaking_rate=0.92,
        volume_gain_db=0.0,
    ),
    # Qat'iyatli yigit ovozi — chaqqon, baquvvat ton
    "male_energetic": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=2.0,
        speaking_rate=1.1,
        volume_gain_db=1.0,
    ),
    # Quvnoq bola ovozi — balandroq va tezroq ton
    "child_playful": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=8.0,
        speaking_rate=1.15,
        volume_gain_db=1.5,
    ),
    # Yangi O'zbek milliy ovozlari (Edge-TTS fallback profillari)
    "lola": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=0.0,
        speaking_rate=0.95,
        volume_gain_db=0.0,
    ),
    "madina": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=0.0,
        speaking_rate=1.0,
        volume_gain_db=0.0,
    ),
    "nozima": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=1.0,
        speaking_rate=0.98,
        volume_gain_db=0.0,
    ),
    "kamola": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=2.0,
        speaking_rate=1.02,
        volume_gain_db=0.5,
    ),
    "safiya": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=-1.0,
        speaking_rate=0.92,
        volume_gain_db=-0.5,
    ),
    "dilnoza": VoiceProfile(
        voice_name_uz="uz-UZ-MadinaNeural",
        voice_name_ru="ru-RU-SvetlanaNeural",
        pitch=3.0,
        speaking_rate=1.05,
        volume_gain_db=0.5,
    ),
    "davron": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=0.0,
        speaking_rate=1.0,
        volume_gain_db=0.0,
    ),
    "amir": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=-2.0,
        speaking_rate=0.96,
        volume_gain_db=0.0,
    ),
    "sardor": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=0.0,
        speaking_rate=1.0,
        volume_gain_db=0.0,
    ),
    "jasur": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=2.0,
        speaking_rate=1.05,
        volume_gain_db=0.5,
    ),
    "javohir": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=-4.0,
        speaking_rate=0.92,
        volume_gain_db=1.0,
    ),
    "abdulhay": VoiceProfile(
        voice_name_uz="uz-UZ-SardorNeural",
        voice_name_ru="ru-RU-DmitryNeural",
        pitch=-1.0,
        speaking_rate=0.95,
        volume_gain_db=0.0,
    ),
}

# Standart profil
DEFAULT_VOICE_TYPE = "female_warm"
