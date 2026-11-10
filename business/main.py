"""Qadirdon AI — Telegram Business Bot kirish nuqtasi."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from business.handlers import all_business_routers
from config.settings import settings


def create_business_bot() -> tuple[Bot, Dispatcher]:
    token = settings.BUSINESS_BOT_TOKEN or settings.effective_bot_token
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    for router in all_business_routers:
        dp.include_router(router)

    return bot, dp


async def start_business_bot():
    bot, dp = create_business_bot()
    logger.info("📱 Business Bot polling rejimida ishga tushirilmoqda...")
    await dp.start_polling(bot)
