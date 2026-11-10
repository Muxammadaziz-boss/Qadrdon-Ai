"""Foydalanuvchi modeli."""

from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Telegram foydalanuvchisi — Qadirdon AI egasi."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(256), default="")
    language: Mapped[str] = mapped_column(String(5), default="uz")
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Foydalanuvchi hisob balansi (so'mda)
    balance: Mapped[int] = mapped_column(BigInteger, default=0)

    # Telegram Business ulanish identifikatori (business_connection_id)
    business_connection_id: Mapped[str | None] = mapped_column(
        String(256), nullable=True, index=True
    )

    # Relationships
    ai_profiles = relationship("AiProfile", back_populates="user", lazy="selectin")
    conversations = relationship("Conversation", back_populates="user", lazy="select")
    contacts = relationship("Contact", back_populates="user", lazy="select")
    subscription = relationship(
        "Subscription", back_populates="user", uselist=False, lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, balance={self.balance})>"
