"""AI profil modeli — har bir foydalanuvchining AI sozlamalari."""

from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base, TimestampMixin


class AiProfile(Base, TimestampMixin):
    """AI shaxsiyati — rol, ism, xarakter, ovoz sozlamalari."""

    __tablename__ = "ai_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # --- Rol ---
    role: Mapped[str] = mapped_column(
        String(20), default="aka"
    )  # aka, uka, opa, singil, ona, qiz_dost, ayol

    # --- Shaxsiyat ---
    ai_name: Mapped[str] = mapped_column(String(64), default="Qadirdon")
    personality_prompt: Mapped[str] = mapped_column(
        Text,
        default="Samimiy, mehribon va g'amxo'r shaxs.",
    )

    # --- Yozish uslubi ---
    emoji_level: Mapped[int] = mapped_column(
        Integer, default=2
    )  # 1=kam, 2=o'rta, 3=ko'p
    typing_speed: Mapped[int] = mapped_column(
        Integer, default=2
    )  # 1=sekin, 2=normal, 3=tez
    use_typos: Mapped[bool] = mapped_column(Boolean, default=True)
    use_slang: Mapped[bool] = mapped_column(Boolean, default=True)
    message_splitting: Mapped[bool] = mapped_column(
        Boolean, default=True
    )  # Xabarni bo'lib yuborish

    # --- Ovoz ---
    voice_type: Mapped[str] = mapped_column(
        String(30), default="male_warm"
    )  # Ovoz profili
    voice_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # --- Maxsus so'zlar ---
    # Masalan: {"greeting": "Salom ukaginam!", "farewell": "Xayr, o'zingni ehtiyot qil!"}
    custom_phrases: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # --- Status va Muloqot Darajasi ---
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    relationship_level: Mapped[int] = mapped_column(Integer, default=1)  # 1..5
    trust_xp: Mapped[int] = mapped_column(Integer, default=0)  # 0..1000
    game_mode: Mapped[str] = mapped_column(String(20), default="story")  # "story" (zabt etish) | "classic" (erkin)
    character_id: Mapped[str | None] = mapped_column(String(50), nullable=True)  # model ID: rayhona, kamola, ...
    unlocked_secrets: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)

    # Relationships
    user = relationship("User", back_populates="ai_profiles")

    def __repr__(self) -> str:
        return f"<AiProfile(id={self.id}, role={self.role}, name={self.ai_name})>"

