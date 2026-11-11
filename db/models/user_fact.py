"""Foydalanuvchi haqidagi uzoq muddatli faktlar modeli."""

from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base, TimestampMixin


class UserFact(Base, TimestampMixin):
    """Foydalanuvchi haqida suhbatdan ajratib olingan doimiy xotira faktlari."""

    __tablename__ = "user_facts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    conversation_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Toifa: name, city, job, preference, event, family, hobby
    category: Mapped[str] = mapped_column(String(50), default="general")
    fact_key: Mapped[str] = mapped_column(String(100), index=True)
    fact_value: Mapped[str] = mapped_column(String(500))

    # Relationships
    user = relationship("User")
    conversation = relationship("Conversation")

    def __repr__(self) -> str:
        return f"<UserFact(user={self.user_id}, {self.fact_key}={self.fact_value})>"
