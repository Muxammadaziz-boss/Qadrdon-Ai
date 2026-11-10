"""Qadirdon AI — Markaziy sozlamalar."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Barcha muhit o'zgaruvchilarini boshqaradi."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Telegram Bot ---
    # Bitta bot orqali ham sozlash, ham Telegram Business shaxsiy profil boshqaruvi ishlaydi!
    BOT_TOKEN: str
    BUSINESS_BOT_TOKEN: str = ""

    # --- Admin va To'lov sozlamalari ---
    # Vergul bilan ajratilgan Telegram ID lar (masalan: 12345678,87654321)
    ADMIN_IDS: str = ""
    ADMIN_USERNAME: str = "@admin"
    CARD_NUMBER: str = "8600 0000 0000 0000"
    CARD_HOLDER: str = "Qadirdon AI"

    # --- Pyrogram (VoIP / Ovozli qo'ng'iroq) ---
    TELEGRAM_API_ID: int = 0
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_PHONE: str = ""

    # --- AI (Google Gemini) ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"

    # --- Google Cloud (TTS / STT) ---
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # --- Database ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./qadirdon_ai.db"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Server ---
    WEBHOOK_URL: str = ""
    WEBHOOK_PORT: int = 8443
    WEBHOOK_SECRET: str = "qadirdon-secret"

    # --- App ---
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    @property
    def effective_bot_token(self) -> str:
        """Asosiy bot tokeni."""
        return self.BOT_TOKEN

    @property
    def admin_id_list(self) -> list[int]:
        """Adminlarning Telegram ID larini ro'yxat ko'rinishida qaytaradi."""
        if not self.ADMIN_IDS:
            return []
        ids = []
        for x in self.ADMIN_IDS.split(","):
            cleaned = x.strip()
            if cleaned.isdigit():
                ids.append(int(cleaned))
        return ids

    @property
    def db_url_async(self) -> str:
        """Asinxron SQLAlchemy uchun to'g'rilangan DB URL."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)

        # asyncpg uchun moslash: sslmode -> ssl, channel_binding ni tozalash
        if "sslmode=" in url:
            url = url.replace("sslmode=require", "ssl=require").replace("sslmode=prefer", "ssl=prefer")
        if "channel_binding=" in url:
            import re
            url = re.sub(r"[?&]channel_binding=[^&]+", "", url)
            if "?" not in url and "&" in url:
                url = url.replace("&", "?", 1)
        return url

    @property
    def db_url_sync(self) -> str:
        """Sinxron DB URL (Alembic uchun)."""
        return self.DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", "")


settings = Settings()
