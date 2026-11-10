"""Qadirdon AI — Telegram Business Ulanish handleri.

Foydalanuvchi botni o'zining Telegram Business sozlamalariga
qo'shganda yoki uzganda bu handler ishlaydi.
"""

from __future__ import annotations

from aiogram import Bot, Router, types
from loguru import logger
from sqlalchemy import select

from db.models import User
from db.session import async_session

business_connection_router = Router(name="business_connection")


@business_connection_router.business_connection()
async def handle_business_connection(
    connection: types.BusinessConnection, bot: Bot
) -> None:
    """Telegram Business ulanish holatini saqlaydi va foydalanuvchiga xabar beradi."""
    conn_id = connection.id
    user_tg_id = connection.user.id
    is_enabled = connection.is_enabled
    can_reply = connection.can_reply

    logger.info(
        "Business connection yangilanishi: conn_id={}, user_id={}, enabled={}, can_reply={}",
        conn_id,
        user_tg_id,
        is_enabled,
        can_reply,
    )

    async with async_session() as session:
        stmt = select(User).where(User.telegram_id == user_tg_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            # Yangi foydalanuvchi bo'lsa yaratamiz
            user = User(
                telegram_id=user_tg_id,
                username=connection.user.username,
                full_name=connection.user.full_name or "",
                business_connection_id=conn_id if is_enabled else None,
            )
            session.add(user)
        else:
            user.business_connection_id = conn_id if is_enabled else None

        await session.commit()

    # Foydalanuvchining shaxsiy bot chatiga xabar yuborish
    try:
        if is_enabled:
            msg_text = (
                "🎉 <b>Telegram Business muvaffaqiyatli ulandi!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "✅ Endi shaxsiy profilingizga boshqalar yozganda, "
                "Qadirdon AI siz tanlagan rol va uslubda xuddi insondek javob qaytaradi!\n\n"
                "💡 <i>Eslatma: AI faoliyatini bot sozlamalari orqali istalgan vaqtda "
                "yoqishingiz yoki o'chirishingiz mumkin.</i>"
            )
        else:
            msg_text = (
                "ℹ️ <b>Telegram Business ulanishi uzildi.</b>\n"
                "Qadirdon AI endi shaxsiy profilingizdan javob bermaydi."
            )

        await bot.send_message(chat_id=user_tg_id, text=msg_text, parse_mode="HTML")
    except Exception as exc:
        logger.warning(
            "Foydalanuvchiga ulanish xabari yuborishda xatolik: {}", exc
        )

