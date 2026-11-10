"""Suhbat modeli — har bir kontakt bilan alohida suhbat."""

from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base, TimestampMixin


class Conversation(Base, TimestampMixin):
    """Foydalanuvchi profili va begona odam o'rtasidagi suhbat."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Begona odam ma'lumotlari
    contact_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    contact_name: Mapped[str] = mapped_column(String(256), default="")

    # Business connection
    business_connection_id: Mapped[str] = mapped_column(String(256), index=True)

    # Kontekst
    last_context_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", lazy="selectin", order_by="Message.id"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, contact={self.contact_telegram_id})>"

