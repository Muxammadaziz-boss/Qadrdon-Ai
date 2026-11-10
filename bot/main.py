"""Qadirdon AI — Asosiy Yagona Bot kirish nuqtasi.

Bitta bot orqali:
1. Foydalanuvchi menyusi va AI sozlamalari
2. Admin kabineti (/admin) va to'lov tizimi
3. Telegram Business shaxsiy profil boshqaruvi (business_connection, business_message)
birgalikda to'liq ishlaydi.
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from bot.handlers import all_bot_routers
from bot.middlewares.auth import AuthMiddleware
from business.handlers import all_business_routers
from config.settings import settings


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Bot va Dispatcher ni yaratadi va barcha routerlarni ulaydi."""
    bot = Bot(
        token=settings.effective_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # 1. Autentifikatsiya middleware lari
    auth_middleware = AuthMiddleware()
    dp.message.middleware(auth_middleware)
    dp.callback_query.middleware(auth_middleware)

    # 2. Foydalanuvchi va Admin routerlari
    for router in all_bot_routers:
        dp.include_router(router)

    # 3. Telegram Business API routerlari (shaxsiy profildan yozish)
    for router in all_business_routers:
        dp.include_router(router)

    return bot, dp


async def start_bot() -> None:
    """Yagona botni polling rejimida ishga tushiradi."""
    bot, dp = create_bot_and_dispatcher()
    logger.info("🤖 Qadirdon AI (Yagona Bot) ishga tushirilmoqda...")

    # Barcha ishlatilgan update turlarini aniqlab Telegramdan so'rash
    used_updates = dp.resolve_used_update_types()
    # Qo'shimcha Telegram Business update turlari
    if "business_connection" not in used_updates:
        used_updates.append("business_connection")
    if "business_message" not in used_updates:
        used_updates.append("business_message")

    logger.info("Qabul qilinadigan update turlari: {}", used_updates)
    await dp.start_polling(bot, allowed_updates=used_updates)
