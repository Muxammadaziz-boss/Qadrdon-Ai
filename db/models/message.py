"""Xabar modeli — suhbat tarixini saqlash."""

from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base, TimestampMixin


class Message(Base, TimestampMixin):
    """Suhbatdagi bitta xabar."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
    )

    # Xabar ma'lumotlari
    role: Mapped[str] = mapped_column(
        String(10)
    )  # "user" (begona odam) yoki "assistant" (AI)
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[str] = mapped_column(
        String(20), default="text"
    )  # text, voice, photo, sticker

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, type={self.message_type})>"

