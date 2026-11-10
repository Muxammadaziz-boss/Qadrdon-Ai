"""Qadirdon AI — Business bot handlerlari."""

from business.handlers.connection import business_connection_router
from business.handlers.message import business_message_router
from business.handlers.photo import photo_router
from business.handlers.reaction import reaction_router
from business.handlers.sticker import sticker_router
from business.handlers.voice_message import voice_message_router

all_business_routers = [
    business_connection_router,
    business_message_router,
    photo_router,
    voice_message_router,
    sticker_router,
    reaction_router,
]

__all__ = [
    "business_connection_router",
    "business_message_router",
    "voice_message_router",
    "photo_router",
    "sticker_router",
    "reaction_router",
    "all_business_routers",
]
