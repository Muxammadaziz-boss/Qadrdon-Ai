"""Qadirdon AI — Barcha sozlash bot routerlarini birlashtirish."""

from bot.handlers.start import start_router
from bot.handlers.setup_role import setup_role_router
from bot.handlers.setup_name import setup_name_router
from bot.handlers.setup_personality import setup_personality_router
from bot.handlers.setup_language import setup_language_router
from bot.handlers.setup_voice import setup_voice_router
from bot.handlers.settings import settings_router
from bot.handlers.premium import premium_router
from bot.handlers.admin import admin_router
from bot.handlers.chat import chat_router

all_bot_routers = [
    start_router,
    admin_router,
    setup_role_router,
    setup_name_router,
    setup_personality_router,
    setup_language_router,
    setup_voice_router,
    settings_router,
    premium_router,
    chat_router,
]

__all__ = ["all_bot_routers"]
