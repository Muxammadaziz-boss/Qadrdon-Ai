"""Ma'lumotlar bazasi sessiya boshqaruvchisi."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.settings import settings
from db.models.base import Base

engine = create_async_engine(
    settings.db_url_async,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Ma'lumotlar bazasi jadvallarini yaratadi va kerakli ustunlarni tekshiradi."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            if "sqlite" in settings.DATABASE_URL:
                await conn.execute(text("ALTER TABLE subscriptions ADD COLUMN last_reset_date DATE"))
            else:
                await conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS last_reset_date DATE DEFAULT CURRENT_DATE"))
        except Exception:
            pass  # Ustun mavjud bo'lsa xatolik e'tiborga olinmaydi

        # AiProfile muloqot darajalari va personaj modellari ustunlari
        for col_name, col_sql in [
            ("relationship_level", "INTEGER DEFAULT 1"),
            ("trust_xp", "INTEGER DEFAULT 0"),
            ("game_mode", "VARCHAR(20) DEFAULT 'story'"),
            ("character_id", "VARCHAR(50)"),
            ("unlocked_secrets", "TEXT DEFAULT '[]'"),
            ("proactive_enabled", "BOOLEAN DEFAULT TRUE"),
            ("voice_emotion", "VARCHAR(30) DEFAULT 'auto'"),
        ]:
            try:
                if "sqlite" in settings.DATABASE_URL:
                    await conn.execute(text(f"ALTER TABLE ai_profiles ADD COLUMN {col_name} {col_sql}"))
                else:
                    await conn.execute(text(f"ALTER TABLE ai_profiles ADD COLUMN IF NOT EXISTS {col_name} {col_sql}"))
            except Exception as e:
                pass

        try:
            if "sqlite" in settings.DATABASE_URL:
                await conn.execute(text("ALTER TABLE conversations ADD COLUMN last_proactive_at DATETIME"))
            else:
                await conn.execute(text("ALTER TABLE conversations ADD COLUMN IF NOT EXISTS last_proactive_at TIMESTAMP WITH TIME ZONE"))
        except Exception:
            pass


async def get_session() -> AsyncSession:
    """Yangi sessiya olish."""
    async with async_session() as session:
        yield session

