"""Qadirdon AI — Loyihani ishga tushirish markazi.

Bu skript:
1. Ma'lumotlar bazasi jadvallarini tekshiradi va initsializatsiya qiladi.
2. Qadirdon AI yagona botini ishga tushiradi (Sozlash + Admin kabineti + Telegram Business).
"""

import asyncio
import sys
from loguru import logger

from utils.logger import setup_logger
from db.session import init_db
from bot.main import start_bot


async def main():
    setup_logger()
    logger.info("🚀 Qadirdon AI tizimi ishga tushmoqda...")

    # 1. Bazani tayyorlash
    logger.info("📦 Ma'lumotlar bazasi jadvallari tekshirilmoqda...")
    await init_db()
    logger.info("✅ Ma'lumotlar bazasi tayyor!")

    # 2. Yagona botni ishga tushirish
    try:
        await start_bot()
    except asyncio.CancelledError:
        logger.warning("🛑 Dastur to'xtatildi.")
    except Exception as e:
        logger.critical(f"❌ Kutilmagan xatolik: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Xayr! Qadirdon AI to'xtatildi.")
