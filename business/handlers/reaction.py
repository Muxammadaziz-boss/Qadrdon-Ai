"""Qadirdon AI — Reaktsiya handleri (Business API).

Xabar reaktsiyalarini (emoji) qayta ishlaydi.
"""

from __future__ import annotations

from aiogram import F, Router, types
from loguru import logger

reaction_router = Router(name="reaction")


@reaction_router.business_message(~F.text & ~F.photo & ~F.voice & ~F.sticker)
async def handle_business_reaction(
    message: types.Message,
) -> None:
    """Business API orqali kelgan reaktsiyalarni loglaydi.

    Telegram Business API da reaktsiya alohida update turi sifatida
    kelishi mumkin. Bu handler ularni qayta ishlashga tayyorlaydi.

    Hozirgi bosqichda faqat loglaydi — keyinchalik
    reaktsiyaga qarab AI xulq-atvorini sozlash mumkin
    (masalan, 👎 ko'p bo'lsa uslubni o'zgartirish).
    """
    # Bu handler faqat hech qanday boshqa handler ishlamasa ishlaydi
    # (fallback sifatida). Asosiy reaktsiya logikasi
    # message_reaction update turi orqali ishlaydi.

    # Agar xabarda matn, rasm, ovoz yoki sticker bo'lmasa
    # va boshqa handler ishlamagan bo'lsa — bu fallback
    if (
        message.text
        or message.photo
        or message.voice
        or message.sticker
        or message.video
        or message.document
        or message.animation
    ):
        return  # Boshqa handler uchun — o'tkazib yuboramiz

    business_connection_id = message.business_connection_id
    if not business_connection_id:
        return

    logger.info(
        "Business boshqa xabar turi: connection={}, chat={}, content_type={}",
        business_connection_id,
        message.chat.id,
        message.content_type,
    )
