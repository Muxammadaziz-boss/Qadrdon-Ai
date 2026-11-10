"""Qadirdon AI — Admin Paneli handleri.

Faqat ADMIN_IDS ro'yxatidagi adminlar uchun mo'ljallangan.
/admin buyrug'i orqali kiriladi.
"""

from __future__ import annotations

import asyncio
from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from bot.keyboards.admin import (
    admin_broadcast_confirm_keyboard,
    admin_cancel_keyboard,
    admin_menu_keyboard,
    admin_plans_keyboard,
)
from bot.keyboards.reply import main_menu_keyboard
from bot.states.admin import AdminStates
from config.settings import settings
from db.models import AiProfile, Conversation, Subscription, User
from db.models.subscription import PLAN_LIMITS, PLAN_NAMES
from db.session import async_session

admin_router = Router(name="admin")


def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshiradi."""
    return user_id in settings.admin_id_list


# ── /admin buyrug'i ─────────────────────────────────────────────────────────
@admin_router.message(Command("admin"))
@admin_router.message(F.text == "🔐 Admin Panel (/admin)")
async def cmd_admin(message: types.Message, state: FSMContext) -> None:
    """Admin kabinetini ochadi."""
    if not is_admin(message.from_user.id):
        await message.answer(
            "⛔️ <b>Kechirasiz, sizda admin huquqlari yo'q.</b>",
            reply_markup=main_menu_keyboard(is_admin=False),
            parse_mode="HTML",
        )
        return

    await state.clear()
    text = (
        "🔐 <b>Qadirdon AI — Admin Boshqaruv Paneli</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Xush kelibsiz, Administrator! Kerakli bo'limni tanlang:"
    )
    await message.answer(text, reply_markup=admin_menu_keyboard(), parse_mode="HTML")


# ── Bekor qilish ────────────────────────────────────────────────────────────
@admin_router.callback_query(F.data == "admin:cancel")
async def admin_cancel(call: types.CallbackQuery, state: FSMContext) -> None:
    """Amalni bekor qiladi va menyuga qaytaradi."""
    await state.clear()
    await call.message.edit_text(
        "❌ Amal bekor qilindi.\n\n🔐 <b>Admin Paneli:</b>",
        reply_markup=admin_menu_keyboard(),
        parse_mode="HTML",
    )
    await call.answer()


@admin_router.callback_query(F.data == "admin:exit")
async def admin_exit(call: types.CallbackQuery, state: FSMContext) -> None:
    """Admin paneldan chiqish."""
    await state.clear()
    is_adm = is_admin(call.from_user.id)
    await call.message.edit_text("👋 Admin paneldan chiqildi.")
    await call.message.answer(
        "Asosiy menyu:",
        reply_markup=main_menu_keyboard(is_admin=is_adm),
    )
    await call.answer()


# ── 1. Statistika ───────────────────────────────────────────────────────────
@admin_router.callback_query(F.data == "admin:stats")
async def admin_stats(call: types.CallbackQuery) -> None:
    """Umumiy tizim statistikasini ko'rsatadi."""
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    async with async_session() as session:
        # Jami foydalanuvchilar
        total_users = await session.scalar(select(func.count(User.id))) or 0

        # Faol AI profillar
        active_profiles = (
            await session.scalar(
                select(func.count(AiProfile.id)).where(AiProfile.is_active == True)
            )
            or 0
        )

        # Pullik obunachilar
        paid_subs = (
            await session.scalar(
                select(func.count(Subscription.id)).where(
                    Subscription.plan != "free", Subscription.is_active == True
                )
            )
            or 0
        )

        # Jami foydalanuvchilar balansi
        total_balance = await session.scalar(select(func.sum(User.balance))) or 0

        # Telegram Business ulanganlar
        business_users = (
            await session.scalar(
                select(func.count(User.id)).where(
                    User.business_connection_id != None
                )
            )
            or 0
        )

        # Jami suhbatlar
        total_convs = (
            await session.scalar(select(func.count(Conversation.id))) or 0
        )

    text = (
        "📊 <b>Qadirdon AI — Tizim Statistikasi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total_users:,} ta\n"
        f"🤖 <b>Faol AI profillari:</b> {active_profiles:,} ta\n"
        f"📱 <b>Telegram Business ulangan:</b> {business_users:,} ta\n"
        f"💬 <b>Jami shaxsiy suhbatlar:</b> {total_convs:,} ta\n\n"
        f"💎 <b>Pullik obunachilar:</b> {paid_subs:,} ta\n"
        f"💰 <b>Foydalanuvchilar jami balansi:</b> {total_balance:,} so'm\n"
    )
    await call.message.edit_text(
        text, reply_markup=admin_menu_keyboard(), parse_mode="HTML"
    )
    await call.answer()


# ── 2. Pul qo'shish (Hisob to'ldirish) ───────────────────────────────────────
@admin_router.callback_query(F.data == "admin:add_balance")
async def start_add_balance(call: types.CallbackQuery, state: FSMContext) -> None:
    """Foydalanuvchi hisobiga pul qo'shish jarayonini boshlaydi."""
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_user_id_for_balance)
    text = (
        "💰 <b>Foydalanuvchi hisobini to'ldirish</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Foydalanuvchining <b>Telegram ID</b> raqamini kiriting:\n\n"
        "<i>(Masalan: 123456789)</i>"
    )
    await call.message.edit_text(
        text, reply_markup=admin_cancel_keyboard(), parse_mode="HTML"
    )
    await call.answer()


@admin_router.message(AdminStates.waiting_for_user_id_for_balance)
async def process_user_id_for_balance(
    message: types.Message, state: FSMContext
) -> None:
    """Kiritilgan User ID ni tekshiradi va topadi."""
    raw_id = message.text.strip()
    if not raw_id.isdigit():
        await message.answer(
            "❌ Noto'g'ri ID kiritildi. Faqat raqamlardan iborat bo'lishi kerak. Qaytadan kiriting:",
            reply_markup=admin_cancel_keyboard(),
        )
        return

    target_tg_id = int(raw_id)
    async with async_session() as session:
        stmt = (
            select(User)
            .where(User.telegram_id == target_tg_id)
            .options(selectinload(User.subscription))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        await message.answer(
            f"❌ <b>ID: {target_tg_id}</b> bo'lgan foydalanuvchi bazadan topilmadi.\n"
            "Foydalanuvchi botga kamida bir marta /start bosgan bo'lishi kerak.",
            reply_markup=admin_cancel_keyboard(),
            parse_mode="HTML",
        )
        return

    await state.update_data(target_user_id=user.id, target_tg_id=user.telegram_id)
    await state.set_state(AdminStates.waiting_for_amount)

    text = (
        f"👤 <b>Foydalanuvchi topildi:</b>\n"
        f"• <b>Ism:</b> {user.full_name}\n"
        f"• <b>Username:</b> @{user.username or 'yo\'q'}\n"
        f"• <b>Telegram ID:</b> <code>{user.telegram_id}</code>\n"
        f"• <b>Joriy balans:</b> {user.balance:,} so'm\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Endi qo'shiladigan summani so'mda kiriting (masalan: <b>50000</b> yoki ayirish uchun <b>-20000</b>):"
    )
    await message.answer(
        text, reply_markup=admin_cancel_keyboard(), parse_mode="HTML"
    )


@admin_router.message(AdminStates.waiting_for_amount)
async def process_amount_for_balance(
    message: types.Message, state: FSMContext, bot: Bot
) -> None:
    """Summani qabul qiladi va foydalanuvchi balansiga qo'shadi."""
    raw_amount = message.text.strip().replace(" ", "").replace(",", "")
    try:
        amount = int(raw_amount)
    except ValueError:
        await message.answer(
            "❌ Noto'g'ri summa kiritildi. Raqam kiriting (masalan: 50000):",
            reply_markup=admin_cancel_keyboard(),
        )
        return

    data = await state.get_data()
    target_user_id = data["target_user_id"]
    target_tg_id = data["target_tg_id"]

    async with async_session() as session:
        stmt = select(User).where(User.id == target_user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi.")
            await state.clear()
            return

        user.balance += amount
        if user.balance < 0:
            user.balance = 0
        new_balance = user.balance
        await session.commit()

    await state.clear()

    # Adminga muvaffaqiyat xabari
    admin_text = (
        f"✅ <b>Balans muvaffaqiyatli yangilandi!</b>\n\n"
        f"👤 Foydalanuvchi: {user.full_name} (ID: <code>{user.telegram_id}</code>)\n"
        f"➕ Qo'shilgan summa: {amount:,} so'm\n"
        f"💳 Yangi balans: <b>{new_balance:,} so'm</b>"
    )
    await message.answer(
        admin_text, reply_markup=admin_menu_keyboard(), parse_mode="HTML"
    )

    # Foydalanuvchiga bot orqali avtomatik bildirishnoma
    try:
        user_notification = (
            "🎉 <b>Hisobingiz to'ldirildi!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Qo'shilgan summa: <b>+{amount:,} so'm</b>\n"
            f"💳 Joriy balansingiz: <b>{new_balance:,} so'm</b>\n\n"
            "Endi <b>'💰 Balans va Tariflar'</b> bo'limi orqali o'zingizga yoqqan tarifni xarid qilishingiz mumkin! 🚀"
        )
        await bot.send_message(
            chat_id=target_tg_id, text=user_notification, parse_mode="HTML"
        )
    except Exception as exc:
        logger.warning(
            "Foydalanuvchiga balans xabarnomasi yetkazilmadi: {}", exc
        )


# ── 3. Obuna berish ─────────────────────────────────────────────────────────
@admin_router.callback_query(F.data == "admin:give_plan")
async def start_give_plan(call: types.CallbackQuery, state: FSMContext) -> None:
    """Foydalanuvchiga to'g'ridan-to'g'ri obuna berishni boshlaydi."""
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_user_id_for_plan)
    text = (
        "💎 <b>Foydalanuvchiga Obuna berish</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Obuna beriladigan foydalanuvchining <b>Telegram ID</b> raqamini kiriting:"
    )
    await call.message.edit_text(
        text, reply_markup=admin_cancel_keyboard(), parse_mode="HTML"
    )
    await call.answer()


@admin_router.message(AdminStates.waiting_for_user_id_for_plan)
async def process_user_id_for_plan(
    message: types.Message, state: FSMContext
) -> None:
    """Obuna berish uchun kiritilgan ID ni tekshiradi."""
    raw_id = message.text.strip()
    if not raw_id.isdigit():
        await message.answer(
            "❌ Faqat raqam kiriting:", reply_markup=admin_cancel_keyboard()
        )
        return

    target_tg_id = int(raw_id)
    async with async_session() as session:
        stmt = (
            select(User)
            .where(User.telegram_id == target_tg_id)
            .options(selectinload(User.subscription))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        await message.answer(
            f"❌ ID: {target_tg_id} bo'lgan foydalanuvchi topilmadi.",
            reply_markup=admin_cancel_keyboard(),
        )
        return

    await state.clear()
    current_plan = user.subscription.plan if user.subscription else "free"
    text = (
        f"👤 <b>Foydalanuvchi:</b> {user.full_name} (ID: <code>{user.telegram_id}</code>)\n"
        f"📦 <b>Joriy tarif:</b> {PLAN_NAMES.get(current_plan, current_plan)}\n\n"
        "Quyidagi tariflardan birini tanlang (avtomatik 30 kunga faollashadi):"
    )
    await message.answer(
        text,
        reply_markup=admin_plans_keyboard(user.telegram_id),
        parse_mode="HTML",
    )


@admin_router.callback_query(F.data.startswith("admin_plan:"))
async def process_plan_selection(call: types.CallbackQuery, bot: Bot) -> None:
    """Tanlangan tarifni foydalanuvchiga biriktiradi."""
    parts = call.data.split(":")
    plan = parts[1]
    target_tg_id = int(parts[2])

    async with async_session() as session:
        stmt = (
            select(User)
            .where(User.telegram_id == target_tg_id)
            .options(selectinload(User.subscription))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            await call.answer("Foydalanuvchi topilmadi!", show_alert=True)
            return

        if user.subscription is None:
            user.subscription = Subscription(user_id=user.id)
            session.add(user.subscription)

        user.subscription.activate_plan(plan, days=30)
        user.is_premium = (plan != "free")
        await session.commit()

    plan_name = PLAN_NAMES.get(plan, plan)
    await call.message.edit_text(
        f"✅ <b>{user.full_name}</b> foydalanuvchisiga <b>{plan_name}</b> tarifi 30 kunga muvaffaqiyatli berildi!",
        reply_markup=admin_menu_keyboard(),
        parse_mode="HTML",
    )
    await call.answer()

    # Foydalanuvchiga xabarnoma
    try:
        user_msg = (
            f"🎉 <b>Tabriklaymiz! Sizga {plan_name} tarifi berildi!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Obuna muddati: <b>30 kun</b>\n"
            "Barcha imkoniyatlar faollashtirildi! 🚀"
        )
        await bot.send_message(
            chat_id=target_tg_id, text=user_msg, parse_mode="HTML"
        )
    except Exception as exc:
        logger.warning("Foydalanuvchiga obuna xabari yetkazilmadi: {}", exc)


# ── 4. Foydalanuvchini qidirish ─────────────────────────────────────────────
@admin_router.callback_query(F.data == "admin:find_user")
async def start_find_user(call: types.CallbackQuery, state: FSMContext) -> None:
    """Foydalanuvchi ma'lumotlarini qidirish."""
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_user_id_search)
    text = (
        "🔍 <b>Foydalanuvchi qidirish</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Qidirilayotgan foydalanuvchining <b>Telegram ID</b> raqamini kiriting:"
    )
    await call.message.edit_text(
        text, reply_markup=admin_cancel_keyboard(), parse_mode="HTML"
    )
    await call.answer()


@admin_router.message(AdminStates.waiting_for_user_id_search)
async def process_user_search(message: types.Message, state: FSMContext) -> None:
    """Foydalanuvchi ma'lumotlarini to'liq chiqaradi."""
    raw_id = message.text.strip()
    if not raw_id.isdigit():
        await message.answer(
            "❌ Faqat raqam kiriting:", reply_markup=admin_cancel_keyboard()
        )
        return

    target_tg_id = int(raw_id)
    async with async_session() as session:
        stmt = (
            select(User)
            .where(User.telegram_id == target_tg_id)
            .options(
                selectinload(User.ai_profiles),
                selectinload(User.subscription),
                selectinload(User.conversations),
            )
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if not user:
        await message.answer(
            f"❌ ID: {target_tg_id} bo'lgan foydalanuvchi topilmadi.",
            reply_markup=admin_cancel_keyboard(),
        )
        return

    await state.clear()

    profile = user.ai_profiles[0] if user.ai_profiles else None
    role_name = profile.role if profile else "Tanlanmagan"
    ai_name = profile.ai_name if profile else "Yo'q"
    plan_name = user.subscription.plan if user.subscription else "free"
    business_status = (
        "🟢 Ulangan" if user.business_connection_id else "🔴 Ulanmagan"
    )

    info_text = (
        f"📋 <b>Foydalanuvchi ma'lumotlari:</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Ism:</b> {user.full_name}\n"
        f"🔗 <b>Username:</b> @{user.username or 'yo\'q'}\n"
        f"🆔 <b>Telegram ID:</b> <code>{user.telegram_id}</code>\n"
        f"💰 <b>Balans:</b> {user.balance:,} so'm\n"
        f"📦 <b>Obuna tarifi:</b> {PLAN_NAMES.get(plan_name, plan_name)}\n"
        f"📱 <b>Telegram Business:</b> {business_status}\n\n"
        f"🤖 <b>AI profili:</b>\n"
        f"• Rol: <b>{role_name}</b>\n"
        f"• AI ismi: <b>{ai_name}</b>\n"
        f"• Holat: {'🟢 Faol' if (profile and profile.is_active) else '🔴 Faol emas'}\n\n"
        f"💬 <b>Suhbatlar soni:</b> {len(user.conversations)} ta\n"
        f"📅 <b>Ro'yxatdan o'tgan:</b> {user.created_at.strftime('%Y-%m-%d %H:%M')}"
    )
    await message.answer(
        info_text, reply_markup=admin_menu_keyboard(), parse_mode="HTML"
    )


# ── 5. Xabar tarqatish (Broadcast) ──────────────────────────────────────────
@admin_router.callback_query(F.data == "admin:broadcast")
async def start_broadcast(call: types.CallbackQuery, state: FSMContext) -> None:
    """Broadcast xabar yuborishni boshlaydi."""
    if not is_admin(call.from_user.id):
        await call.answer("Ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_broadcast_text)
    text = (
        "📢 <b>Barcha foydalanuvchilarga xabar yuborish</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Yubormoqchi bo'lgan xabaringiz matnini yuboring (rasm, video yoki oddiy matn):"
    )
    await call.message.edit_text(
        text, reply_markup=admin_cancel_keyboard(), parse_mode="HTML"
    )
    await call.answer()


@admin_router.message(AdminStates.waiting_for_broadcast_text)
async def process_broadcast_text(message: types.Message, state: FSMContext) -> None:
    """Broadcast matnini saqlaydi va tasdiq so'raydi."""
    broadcast_content = message.text or message.caption or ""
    if not broadcast_content:
        await message.answer("⚠️ Iltimos, xabar matnini yuboring:", reply_markup=admin_cancel_keyboard())
        return

    await state.update_data(broadcast_text=broadcast_content)
    await state.set_state(AdminStates.confirm_broadcast)

    preview_text = (
        "📢 <b>Xabar ko'rinishi:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{broadcast_content}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Ushbu xabarni barcha foydalanuvchilarga yuborishni tasdiqlaysizmi?"
    )
    try:
        await message.answer(
            preview_text,
            reply_markup=admin_broadcast_confirm_keyboard(),
            parse_mode="HTML",
        )
    except Exception:
        await message.answer(
            preview_text,
            reply_markup=admin_broadcast_confirm_keyboard(),
            parse_mode=None,
        )


@admin_router.callback_query(F.data == "broadcast:confirm")
async def execute_broadcast(
    call: types.CallbackQuery, state: FSMContext, bot: Bot
) -> None:
    """Xabarni barcha foydalanuvchilarga tarqatadi."""
    data = await state.get_data()
    broadcast_text = data.get("broadcast_text")
    await state.clear()

    if not broadcast_text:
        await call.answer("Xabar matni topilmadi!", show_alert=True)
        return

    await call.message.edit_text("⏳ Xabar tarqatilmoqda, iltimos kuting...")

    async with async_session() as session:
        users = (await session.scalars(select(User.telegram_id))).all()

    sent = 0
    failed = 0
    for tg_id in users:
        try:
            try:
                await bot.send_message(
                    chat_id=tg_id, text=broadcast_text, parse_mode="HTML"
                )
            except Exception:
                # HTML parse xatosi bo'lsa oddiy matn sifatida qayta jo'natish
                await bot.send_message(
                    chat_id=tg_id, text=broadcast_text, parse_mode=None
                )
            sent += 1
            await asyncio.sleep(0.04)  # Telegram limitlariga tushmaslik uchun
        except Exception:
            failed += 1

    report_text = (
        f"📢 <b>Xabar tarqatish yakunlandi!</b>\n\n"
        f"✅ Muvaffaqiyatli yetkazildi: <b>{sent} ta</b>\n"
        f"❌ Yetib bormadi (bloklangan): <b>{failed} ta</b>"
    )
    await call.message.edit_text(
        report_text, reply_markup=admin_menu_keyboard(), parse_mode="HTML"
    )
    await call.answer()

