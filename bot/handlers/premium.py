"""Qadirdon AI — Balans va Obuna handleri.

Foydalanuvchi balansi, tarif rejalari va xarid qilish.
Admin orqali to'lov tizimi.
"""

from __future__ import annotations

from aiogram import F, Router, types
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.keyboards.inline import balance_keyboard
from config.settings import settings
from db.models import Subscription, User
from db.models.subscription import PLAN_NAMES, PLAN_PRICES
from db.session import async_session

premium_router = Router(name="premium")


def _get_balance_text(user: User) -> str:
    """Balans va obuna holati matnini formatlaydi."""
    sub = user.subscription
    plan_code = sub.plan if sub else "free"
    plan_name = PLAN_NAMES.get(plan_code, "Bepul (Start)")

    exp_str = "Cheksiz"
    if sub and sub.expires_at and plan_code != "free":
        exp_str = sub.expires_at.strftime("%Y-%m-%d %H:%M")

    used = sub.daily_messages_used if sub else 0
    limit = sub.daily_messages_limit if sub else 50
    limit_str = "Cheksiz" if plan_code in ("premium", "ultra") else f"{used}/{limit} ta"

    return (
        "💰 <b>Qadirdon AI — Mening Hisobim va Tariflar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 <b>Sizning ID:</b> <code>{user.telegram_id}</code>\n"
        f"💳 <b>Hisob balansingiz:</b> <b>{user.balance:,} so'm</b>\n"
        f"📦 <b>Joriy tarifingiz:</b> <b>{plan_name}</b>\n"
        f"⏳ <b>Amal qilish muddati:</b> {exp_str}\n"
        f"✉️ <b>Bugungi xabarlar:</b> {limit_str}\n\n"
        "💎 <b>Mavjud Tarif Rejalari:</b>\n"
        "• <b>Standard</b> — 35,000 so'm / oy (200 ta xabar/kun, 3 ta rol)\n"
        "• <b>Premium</b> — 75,000 so'm / oy (Cheksiz xabarlar, barcha 7 rol, ovozli xabarlar)\n"
        "• <b>Ultra VIP</b> — 150,000 so'm / oy (Barcha imkoniyatlar + VoIP Ovozli Qo'ng'iroq)\n\n"
        "<i>Hisobingizni to'ldirib, quyidagi tugmalar orqali obunani bir zumda faollashtirishingiz mumkin.</i>"
    )


# ── Balans bo'limini ochish ─────────────────────────────────────────────────
@premium_router.message(F.text == "💰 Balans va Tariflar")
@premium_router.message(F.text == "💎 Premium")
async def show_balance_menu(message: types.Message) -> None:
    """Mening hisobim va tariflar menyusini ko'rsatadi."""
    async with async_session() as session:
        stmt = (
            select(User)
            .where(User.telegram_id == message.from_user.id)
            .options(selectinload(User.subscription))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        await message.answer("Iltimos, avval /start buyrug'ini bosing.")
        return

    text = _get_balance_text(user)
    await message.answer(text, reply_markup=balance_keyboard(), parse_mode="HTML")


# ── Yangilash ───────────────────────────────────────────────────────────────
@premium_router.callback_query(F.data == "pay:refresh")
async def refresh_balance(call: types.CallbackQuery) -> None:
    """Balans ko'rinishini yangilaydi."""
    async with async_session() as session:
        stmt = (
            select(User)
            .where(User.telegram_id == call.from_user.id)
            .options(selectinload(User.subscription))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        await call.answer("Foydalanuvchi topilmadi!", show_alert=True)
        return

    text = _get_balance_text(user)
    await call.message.edit_text(
        text, reply_markup=balance_keyboard(), parse_mode="HTML"
    )
    await call.answer("🔄 Yangilandi!")


# ── To'lov qilish yo'riqnomasi ──────────────────────────────────────────────
@premium_router.callback_query(F.data == "pay:instructions")
async def show_payment_instructions(call: types.CallbackQuery) -> None:
    """Admin orqali hisob to'ldirish qo'llanmasini ko'rsatadi."""
    text = (
        "💳 <b>Hisobni to'ldirish tartibi (Admin orqali):</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ <b>Quyidagi karta raqamiga to'lov qiling:</b>\n"
        f"💳 Karta raqami: <code>{settings.CARD_NUMBER}</code>\n"
        f"👤 Karta egasi: <b>{settings.CARD_HOLDER}</b>\n\n"
        "2️⃣ <b>To'lov chekini va o'zingizning ID raqamingizni adminga yuboring:</b>\n"
        f"🆔 Sizning ID raqamingiz: <code>{call.from_user.id}</code>\n"
        f"👨‍💻 Administrator: {settings.ADMIN_USERNAME}\n\n"
        "3️⃣ Administrator chekni tekshirib, bir necha daqiqada hisobingizga "
        "mablag' qo'shib beradi va bot sizga xabar beradi!\n\n"
        "4️⃣ Balansingiz to'lgach, kerakli tarif tugmasini bosib obunani faollashtirasiz."
    )
    await call.message.edit_text(
        text, reply_markup=balance_keyboard(), parse_mode="HTML"
    )
    await call.answer()


# ── Balans orqali tarif sotib olish ─────────────────────────────────────────
@premium_router.callback_query(F.data.startswith("buy_plan:"))
async def buy_plan_from_balance(call: types.CallbackQuery) -> None:
    """Foydalanuvchi balansidan pul yechib tarifni faollashtiradi."""
    plan_code = call.data.split(":")[1]
    price = PLAN_PRICES.get(plan_code, 0)
    plan_name = PLAN_NAMES.get(plan_code, plan_code)

    async with async_session() as session:
        async with session.begin():
            stmt = (
                select(User)
                .where(User.telegram_id == call.from_user.id)
                .with_for_update()
                .options(selectinload(User.subscription))
            )
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                await call.answer("Foydalanuvchi topilmadi!", show_alert=True)
                return

            # Balans yetarliligini tekshirish
            if user.balance < price:
                shortage = price - user.balance
                alert_text = (
                    f"⚠️ Balansingizda mablag' yetarli emas!\n\n"
                    f"Kerakli summa: {price:,} so'm\n"
                    f"Sizning balansingiz: {user.balance:,} so'm\n"
                    f"Yetishmayapti: {shortage:,} so'm\n\n"
                    f"Iltimos, avval '💳 Hisobni to'ldirish' tugmasi orqali adminga murojaat qiling."
                )
                await call.answer(alert_text, show_alert=True)
                return

            # Balansdan yechish
            user.balance -= price

            # Obunani faollashtirish
            if user.subscription is None:
                user.subscription = Subscription(user_id=user.id)
                session.add(user.subscription)

            user.subscription.activate_plan(plan_code, days=30)
            user.is_premium = True
            remaining_balance = user.balance

        success_text = (
            f"🎉 <b>Tabriklaymiz! {plan_name} tarifi muvaffaqiyatli xarid qilindi!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Yechilgan summa: <b>{price:,} so'm</b>\n"
            f"💳 Qolgan balans: <b>{remaining_balance:,} so'm</b>\n"
            f"⏳ Obuna muddati: <b>30 kun</b>\n\n"
            "Barcha imkoniyatlar ochildi! Qadirdon AI xizmatingizda. 🚀"
        )
        await call.message.edit_text(
            success_text, reply_markup=balance_keyboard(), parse_mode="HTML"
        )
        await call.answer("🎉 Xarid muvaffaqiyatli yakunlandi!")
        logger.info(
            "Foydalanuvchi obuna sotib oldi: user_id={}, plan={}, price={}",
            user.id,
            plan_code,
            price,
        )
