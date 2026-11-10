"""Obuna modeli — foydalanuvchining to'lov rejasi."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base, TimestampMixin

# Tarif narxlari (so'mda, 30 kun uchun)
PLAN_PRICES: dict[str, int] = {
    "free": 0,
    "standard": 35_000,
    "premium": 75_000,
    "ultra": 150_000,
}

# Tarif nomlari
PLAN_NAMES: dict[str, str] = {
    "free": "Bepul (Start)",
    "standard": "Standard",
    "premium": "Premium",
    "ultra": "Ultra (VIP)",
}

# Kunlik xabar limitlari
PLAN_LIMITS: dict[str, int] = {
    "free": 50,
    "standard": 200,
    "premium": 999_999,  # Cheksiz
    "ultra": 999_999,    # Cheksiz
}


class Subscription(Base, TimestampMixin):
    """Foydalanuvchining obuna holati."""

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )

    plan: Mapped[str] = mapped_column(
        String(20), default="free"
    )  # free, standard, premium, ultra
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Cheklovlar
    daily_messages_used: Mapped[int] = mapped_column(default=0)
    daily_messages_limit: Mapped[int] = mapped_column(default=50)
    last_reset_date: Mapped[date] = mapped_column(Date, default=date.today)

    # Relationships
    user = relationship("User", back_populates="subscription")

    def check_and_reset_daily(self) -> bool:
        """Yangi kun boshlangan bo'lsa kunlik hisoblagichni nollaydi."""
        today = date.today()
        if self.last_reset_date is None or today > self.last_reset_date:
            self.daily_messages_used = 0
            self.last_reset_date = today
            return True
        return False

    @property
    def is_expired(self) -> bool:
        """Obuna muddati tugaganmi."""
        if self.plan == "free":
            return False
        if self.expires_at is None:
            return True
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def can_send_message(self) -> bool:
        """Xabar yuborish limiti bormi."""
        self.check_and_reset_daily()
        used = self.daily_messages_used or 0
        limit = self.daily_messages_limit or PLAN_LIMITS.get(self.plan, 50)

        if self.plan in ("premium", "ultra") and not self.is_expired:
            return True
        if self.is_expired:
            return used < PLAN_LIMITS["free"]
        return used < limit

    def activate_plan(self, plan: str, days: int = 30) -> None:
        """Tarifni faollashtirish yoki muddatini uzaytirish."""
        self.plan = plan
        self.is_active = True
        self.daily_messages_limit = PLAN_LIMITS.get(plan, 50)
        self.daily_messages_used = 0
        self.last_reset_date = datetime.now(timezone.utc).date()

        now = datetime.now(timezone.utc)
        if self.expires_at and self.expires_at > now:
            self.expires_at += timedelta(days=days)
        else:
            self.expires_at = now + timedelta(days=days)

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, plan={self.plan}, active={self.is_active})>"
