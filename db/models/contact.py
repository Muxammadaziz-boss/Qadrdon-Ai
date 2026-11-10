"""Kontakt modeli — foydalanuvchiga yozgan odamlar."""

from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base, TimestampMixin


class Contact(Base, TimestampMixin):
    """Foydalanuvchiga xabar yozgan begona odam haqida ma'lumot."""

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String(256), default="")
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Foydalanuvchi eslatmasi: bu odam kim
    relationship_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="contacts")

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name={self.name})>"

