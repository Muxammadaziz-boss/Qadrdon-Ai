"""Qadirdon AI — Matnli xabar handleri (Business API).

Bu modul Telegram Business API orqali kelgan matnli xabarlarni qabul qiladi,
AI javob generatsiya qiladi va foydalanuvchining shaxsiy profilidan yuboradi.
"""

from __future__ import annotations

import asyncio
import os
import random
import time
from pathlib import Path

from aiogram import Bot, F, Router, types
from aiogram.types import FSInputFile
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ai.engine import AiEngine
from ai.memory.short_term import get_recent_messages, save_recent_message
from ai.trust_evaluator import evaluate_message_trust
from ai.characters import get_character_model
from ai.characters.photo_manager import (
    is_photo_requested,
    get_photo_category,
    get_or_download_photo,
    get_photo_caption,
)
from ai.memory.fact_extractor import extract_facts_from_text, save_extracted_facts
from ai.quests.manager import check_secret_quest_trigger
from business.utils.human_delay import calculate_delay
from business.utils.typing_simulator import simulate_recording_voice, simulate_typing
from business.utils.read_receipt import mark_business_message_as_read
from voice.tts_engine import text_to_speech
from db.models import AiProfile, Contact, Conversation, Message, Subscription, User
from db.session import async_session

business_message_router = Router(name="business_message")

# AI dvigatel — modul darajasida bir marta yaratiladi
_ai_engine = AiEngine()

# Xabar tarixidan nechta xabar olish
_HISTORY_LIMIT = 30

# Obuna limiti tugaganda yuboriladigan xabar
_LIMIT_REACHED_TEXT = (
    "Bugungi xabar limiti tugadi. Qo'shimcha xabar yuborish uchun "
    "obuna rejangizni yangilang. 🔒"
)

# AI xatosi yuz berganda yuboriladigan xabar
_FALLBACK_TEXT = "Kechirasiz, hozir biroz band edim. Sal keyinroq yozsam maylimi? 🙏"

# Tezkor in-memory keshlar (tarmoq kechikishini bartaraf etish uchun)
_BUSINESS_USER_CACHE: dict[str, tuple[float, User]] = {}
_BUSINESS_USER_CACHE_TTL = 60.0  # 60 soniya

_CONV_CACHE: dict[tuple[int, int], Conversation] = {}


async def _get_user_by_business_connection(
    business_connection_id: str,
) -> User | None:
    """Business connection_id bo'yicha foydalanuvchini keshdan yoki bazadan qidiradi."""
    now = time.monotonic()
    cached = _BUSINESS_USER_CACHE.get(business_connection_id)
    if cached and (now - cached[0] < _BUSINESS_USER_CACHE_TTL):
        return cached[1]

    async with async_session() as session:
        # 1. Bevosita user.business_connection_id orqali bitta joined query
        stmt = (
            select(User)
            .where(User.business_connection_id == business_connection_id)
            .options(
                joinedload(User.subscription),
                joinedload(User.ai_profiles),
            )
        )
        result = await session.execute(stmt)
        user = result.unique().scalar_one_or_none()
        if user:
            _BUSINESS_USER_CACHE[business_connection_id] = (now, user)
            return user

        # 2. Agar topilmasa, mavjud Conversation orqali qidirish
        stmt2 = (
            select(User)
            .join(Conversation, Conversation.user_id == User.id)
            .where(Conversation.business_connection_id == business_connection_id)
            .options(
                joinedload(User.subscription),
                joinedload(User.ai_profiles),
            )
            .limit(1)
        )
        result2 = await session.execute(stmt2)
        user = result2.unique().scalar_one_or_none()
        if user:
            _BUSINESS_USER_CACHE[business_connection_id] = (now, user)
        return user


async def _get_active_ai_profile(user: User) -> AiProfile | None:
    """Foydalanuvchining faol AI profilini oladi."""
    for profile in user.ai_profiles:
        if profile.is_active:
            return profile
    return None


async def _check_subscription(user: User) -> bool:
    """Obuna limitini tekshiradi."""
    if user.subscription is None:
        return True  # Obuna yo'q — bepul reja
    return user.subscription.can_send_message


async def _increment_daily_usage(user: User) -> None:
    """Kunlik xabar hisoblagichini oshiradi."""
    if user.subscription is None:
        return
    async with async_session() as session:
        stmt = select(Subscription).where(Subscription.user_id == user.id)
        result = await session.execute(stmt)
        sub = result.scalar_one_or_none()
        if sub:
            sub.daily_messages_used += 1
            await session.commit()


async def _get_or_create_conversation(
    user: User,
    contact_chat_id: int,
    contact_name: str,
    business_connection_id: str,
) -> Conversation:
    """Mavjud suhbatni topadi yoki yangi yaratadi. Keshdan foydalanadi."""
    cache_key = (user.id, contact_chat_id)
    cached_conv = _CONV_CACHE.get(cache_key)
    if cached_conv and cached_conv.business_connection_id == business_connection_id:
        return cached_conv

    async with async_session() as session:
        stmt = select(Conversation).where(
            Conversation.user_id == user.id,
            Conversation.contact_telegram_id == contact_chat_id,
        )
        result = await session.execute(stmt)
        conversation = result.scalar_one_or_none()

        if conversation:
            if conversation.business_connection_id != business_connection_id:
                conversation.business_connection_id = business_connection_id
            if contact_name and not conversation.contact_name:
                conversation.contact_name = contact_name
            await session.commit()
            _CONV_CACHE[cache_key] = conversation
            return conversation

        # Yangi suhbat yaratish
        conversation = Conversation(
            user_id=user.id,
            contact_telegram_id=contact_chat_id,
            contact_name=contact_name,
            business_connection_id=business_connection_id,
            message_count=0,
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        _CONV_CACHE[cache_key] = conversation
        logger.info(
            "Yangi suhbat yaratildi: user_id={}, contact={}",
            user.id,
            contact_chat_id,
        )
        return conversation


async def _get_conversation_history(conversation_id: int) -> list[dict]:
    """Suhbat tarixining oxirgi N xabarini oladi (avval tezkor kesh, keyin SQL)."""
    # 1. Tezkor keshni tekshirish (0 ms)
    recent = await get_recent_messages(conversation_id)
    if recent:
        return recent

    # 2. SQL bazadan yuklash
    async with async_session() as session:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.id.desc())
            .limit(_HISTORY_LIMIT)
        )
        result = await session.execute(stmt)
        messages = list(reversed(result.scalars().all()))

        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        # Keshga saqlash
        for msg in history:
            await save_recent_message(conversation_id, msg["role"], msg["content"])
        return history


async def _save_message(
    conversation_id: int,
    role: str,
    content: str,
    message_type: str = "text",
) -> None:
    """Xabarni bazaga saqlaydi va suhbat hisoblagichini oshiradi."""
    # Avval tezkor xotira keshiga yozamiz
    await save_recent_message(conversation_id, role, content)

    async with async_session() as session:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_type=message_type,
        )
        session.add(msg)

        # Suhbat xabar sonini oshirish
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(stmt)
        conv = result.scalar_one_or_none()
        if conv:
            conv.message_count += 1

        await session.commit()


async def _safe_save_message(
    conversation_id: int,
    role: str,
    content: str,
    message_type: str = "text",
) -> None:
    """Fon rejimida xavfsiz saqlash."""
    try:
        await _save_message(conversation_id, role, content, message_type)
    except Exception as exc:
        logger.error("Xabarni bazaga saqlashda xato: {}", exc)


async def _safe_increment_daily_usage(user: User) -> None:
    """Fon rejimida hisoblagichni oshirish."""
    try:
        await _increment_daily_usage(user)
    except Exception as exc:
        logger.error("Hisoblagichni oshirishda xato: {}", exc)


async def _safe_update_relationship(
    user: User,
    ai_profile: AiProfile,
    user_text: str,
    bot: Bot,
) -> None:
    """Fon rejimida muloqot darajasi va XP ni yangilash hamda lozim bo'lsa tabriklash."""
    try:
        current_xp = getattr(ai_profile, "trust_xp", 0)
        current_lvl = getattr(ai_profile, "relationship_level", 1)
        role = getattr(ai_profile, "role", "aka")
        game_mode = getattr(ai_profile, "game_mode", "story")

        res = evaluate_message_trust(
            user_text=user_text,
            current_xp=current_xp,
            current_level=current_lvl,
            role=role,
            game_mode=game_mode,
        )

        new_xp = res["new_xp"]
        new_lvl = res["new_level"]

        # Yashirin kvestlarni tekshirish
        char_id = getattr(ai_profile, "character_id", None)
        char_model = get_character_model(role, char_id) if char_id else None
        if char_model:
            secret = check_secret_quest_trigger(user_text, char_model, ai_profile.unlocked_secrets)
            if secret:
                new_xp += secret["reward_xp"]
                curr_sec = list(ai_profile.unlocked_secrets or [])
                if secret["id"] not in curr_sec:
                    curr_sec.append(secret["id"])
                    ai_profile.unlocked_secrets = curr_sec
                sec_notify = (
                    f"🗝️ <b>Yashirin sir ochildi: {secret['title']}!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✨ <i>{secret['story']}</i>\n\n"
                    f"🎁 <b>+{secret['reward_xp']} EXP</b> qo'shildi! (Jami: {new_xp} XP)"
                )
                try:
                    await bot.send_message(chat_id=user.telegram_id, text=sec_notify, parse_mode="HTML")
                except Exception:
                    pass

        # Bazada saqlash
        async with async_session() as session:
            stmt = select(AiProfile).where(AiProfile.id == ai_profile.id)
            db_res = await session.execute(stmt)
            p = db_res.scalar_one_or_none()
            if p:
                p.trust_xp = new_xp
                p.relationship_level = new_lvl
                if ai_profile.unlocked_secrets:
                    p.unlocked_secrets = ai_profile.unlocked_secrets
                await session.commit()

        # Profil obyektini keshda ham yangilash
        ai_profile.trust_xp = new_xp
        ai_profile.relationship_level = new_lvl

        # Agar daraja oshgan bo'lsa, egasini xabardor qilish!
        if res["leveled_up"]:
            info = res["level_info"]
            notify_text = (
                f"🎉 <b>Munosabat yangi darajaga ko'tarildi!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎭 <b>AI:</b> {ai_profile.ai_name}\n"
                f"📈 <b>Yangi bosqich:</b> {info['title']}\n"
                f"📝 <i>{info['desc']}</i>\n"
                f"✨ <i>Joriy ball: {new_xp} XP</i>"
            )
            try:
                await bot.send_message(chat_id=user.telegram_id, text=notify_text, parse_mode="HTML")
            except Exception:
                pass
    except Exception as exc:
        logger.error("Munosabat darajasini yangilashda xatolik: {}", exc)


async def _get_contact_info(user: User, contact_telegram_id: int) -> dict | None:
    """Kontakt haqida ma'lumotni alohida to'g'ridan-to'g'ri oladi."""
    async with async_session() as session:
        stmt = (
            select(Contact)
            .where(
                Contact.user_id == user.id,
                Contact.telegram_id == contact_telegram_id,
            )
            .limit(1)
        )
        res = await session.execute(stmt)
        contact = res.scalar_one_or_none()
        if contact:
            return {
                "name": contact.name,
                "username": contact.username,
                "relationship_note": contact.relationship_note,
            }
    return None


@business_message_router.business_message(F.text)
async def handle_business_text_message(message: types.Message, bot: Bot) -> None:
    """Telegram Business API orqali kelgan matnli xabarni qayta ishlaydi."""
    business_connection_id = message.business_connection_id
    chat_id = message.chat.id
    user_text = message.text

    if not business_connection_id:
        return

    logger.info(
        "Business xabar: connection={}, chat={}, text={}",
        business_connection_id,
        chat_id,
        user_text[:50] if user_text else "",
    )

    # 1. Foydalanuvchini topish (keshdan / bazadan)
    user = await _get_user_by_business_connection(business_connection_id)
    if user is None:
        logger.warning(
            "Foydalanuvchi topilmadi: business_connection_id={}",
            business_connection_id,
        )
        return

    # Faqat shaxsiy (private) chatlar bilan ishlash
    if message.chat.type != "private":
        return

    # Profil egasi o'zi yozgan xabarga AI javob bermasligi kerak
    if message.from_user and message.from_user.id == user.telegram_id:
        logger.debug(
            "Profil egasining o'z xabari o'tkazib yuborildi: user_id={}",
            user.telegram_id,
        )
        return

    # 2. Faol AI profilni olish
    ai_profile = await _get_active_ai_profile(user)
    if ai_profile is None or not ai_profile.is_active:
        return

    # 3. Obuna limitini tekshirish
    if not await _check_subscription(user):
        logger.info("Obuna limiti tugadi: user_id={}", user.id)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=_LIMIT_REACHED_TEXT,
                business_connection_id=business_connection_id,
            )
        except Exception as exc:
            logger.error("Limit xabari yuborishda xato: {}", exc)
        return

    # 4. Kelgan xabarni o'qilgan (double true / ✓✓) holatiga o'tkazish
    incoming_message_id = message.message_id
    await mark_business_message_as_read(
        bot=bot,
        business_connection_id=business_connection_id,
        chat_id=chat_id,
        message_id=incoming_message_id,
    )

    # Kontakt ma'lumotlari
    contact_name = ""
    if message.from_user:
        contact_name = message.from_user.full_name or message.from_user.first_name or ""

    # 5. Suhbatni olish/yaratish
    conversation = await _get_or_create_conversation(
        user=user,
        contact_chat_id=chat_id,
        contact_name=contact_name,
        business_connection_id=business_connection_id,
    )

    # 6. Suhbat tarixini olish (keshdan tezkor)
    history = await _get_conversation_history(conversation.id)

    # 7. Foydalanuvchi xabarini fon rejimida bazaga saqlash
    asyncio.create_task(
        _safe_save_message(
            conversation_id=conversation.id,
            role="user",
            content=user_text,
            message_type="text",
        )
    )

    # 7.1 Foydalanuvchi xotira faktlarini ajratib olish va saqlash
    extracted_facts = extract_facts_from_text(user_text)
    if extracted_facts:
        asyncio.create_task(
            save_extracted_facts(
                user_id=user.id,
                conversation_id=conversation.id,
                facts=extracted_facts,
            )
        )

    # 8. AI javob generatsiya qilish
    try:
        ai_response = await _ai_engine.generate_response(
            user_message=user_text,
            conversation_history=history,
            ai_profile=ai_profile,
            contact_name=contact_name,
        )
    except Exception as exc:
        logger.error("AI javob generatsiyasida xato: {}", exc)
        try:
            await simulate_typing(
                bot, chat_id, business_connection_id, _FALLBACK_TEXT,
                typing_speed=ai_profile.typing_speed,
            )
            await bot.send_message(
                chat_id=chat_id,
                text=_FALLBACK_TEXT,
                business_connection_id=business_connection_id,
            )
        except Exception as send_exc:
            logger.error("Fallback xabar yuborishda xato: {}", send_exc)
        return

    response_text: str = ai_response.get("text", "")
    parts: list[str] = ai_response.get("parts", [])
    delay_seconds: float = ai_response.get("delay_seconds", 0.0)
    correction: str | None = ai_response.get("correction")

    # 9. Insoniy qisqa o'qish kechikishi (tezlikka qarab minimal)
    if delay_seconds > 0:
        await asyncio.sleep(min(delay_seconds, 1.0))

    # 10. Javobni yuborish (Rasm, Ovozli yoki Matnli)
    lower_user_text = user_text.lower()
    user_asked_photo = is_photo_requested(user_text)
    photo_sent = False

    if user_asked_photo:
        try:
            role = getattr(ai_profile, "role", "qiz_dost")
            category = get_photo_category(user_text, role=role)
            photo_src = await get_or_download_photo(category)
            photo_caption = get_photo_caption(
                category=category,
                level=getattr(ai_profile, "relationship_level", 1),
                role=role,
                game_mode=getattr(ai_profile, "game_mode", "story"),
            )
            if photo_src.startswith("http"):
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_src,
                    caption=photo_caption,
                    business_connection_id=business_connection_id,
                )
            else:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=FSInputFile(photo_src),
                    caption=photo_caption,
                    business_connection_id=business_connection_id,
                )
            full_response = f"[Rasm: {photo_caption}]"
            photo_sent = True
            logger.info("Rasm muvaffaqiyatli yuborildi: user_id={}, chat_id={}, cat={}", user.id, chat_id, category)
        except Exception as p_err:
            logger.warning("Rasm yuborishda xato: {}, ovoz/matnga o'tilmoqda: {}", p_err)
            photo_sent = False

    VOICE_REQUEST_KEYWORDS = (
        "ovozli", "ovozing", "audio", "gapir", "eshitay",
        "gapirib ber", "ovoz chiqar", "ovoz yubor", "audio yoz",
        "audio tashla", "ovoz tashla", "ovozingizni", "ovozingni",
    )
    user_asked_voice = any(kw in lower_user_text for kw in VOICE_REQUEST_KEYWORDS)
    voice_enabled = getattr(ai_profile, "voice_enabled", False)

    should_send_voice = not photo_sent and (user_asked_voice or (voice_enabled and random.random() < 0.35))
    voice_sent = False

    if should_send_voice:
        try:
            voice_path = await text_to_speech(
                text=response_text,
                voice_type=getattr(ai_profile, "voice_type", "female_warm"),
                language="uz",
                role=getattr(ai_profile, "role", "qiz_dost"),
                level=getattr(ai_profile, "relationship_level", 1),
            )
            # «ovozli xabar yozmoqda...» amali
            record_duration = max(1.5, min(3.5, len(response_text) * 0.04))
            await simulate_recording_voice(bot, chat_id, business_connection_id, duration=record_duration)

            await bot.send_voice(
                chat_id=chat_id,
                voice=FSInputFile(voice_path),
                business_connection_id=business_connection_id,
            )
            full_response = f"[Ovozli xabar: {response_text}]"
            voice_sent = True
            Path(voice_path).unlink(missing_ok=True)
            logger.info("Ovozli javob yuborildi: user_id={}, chat_id={}", user.id, chat_id)
        except Exception as v_err:
            logger.warning("Ovozli xabar yuborishda xato: {}, matnga o'tilmoqda: {}", v_err)
            voice_sent = False

    try:
        if not photo_sent and not voice_sent:
            if len(parts) > 1 and getattr(ai_profile, "message_splitting", True):
                # Bo'lib yuborish
                for i, part in enumerate(parts):
                    await simulate_typing(
                        bot, chat_id, business_connection_id, part,
                        typing_speed=ai_profile.typing_speed,
                    )
                    await bot.send_message(
                        chat_id=chat_id,
                        text=part,
                        business_connection_id=business_connection_id,
                    )

                    if i < len(parts) - 1:
                        inter_delay = calculate_delay(
                            text_length=len(parts[i + 1]),
                            typing_speed=ai_profile.typing_speed,
                        )
                        await asyncio.sleep(min(inter_delay, 1.0))

                full_response = "\n".join(parts)
            else:
                # Bitta xabar
                await simulate_typing(
                    bot, chat_id, business_connection_id, response_text,
                    typing_speed=ai_profile.typing_speed,
                )
                await bot.send_message(
                    chat_id=chat_id,
                    text=response_text,
                    business_connection_id=business_connection_id,
                )
                full_response = response_text

            # Typo correction
            if correction:
                await asyncio.sleep(0.6)
                await bot.send_message(
                    chat_id=chat_id,
                    text=correction,
                    business_connection_id=business_connection_id,
                )
                full_response += f"\n{correction}"

    except Exception as exc:
        logger.error("Javob yuborishda xato: {}", exc)
        return

    # Xabarni qayta o'qilgan (double true / ✓✓) holatiga o'tkazish
    await mark_business_message_as_read(
        bot=bot,
        business_connection_id=business_connection_id,
        chat_id=chat_id,
        message_id=incoming_message_id,
    )

    # 11. AI javobini fon rejimida bazaga saqlash va hisoblagichni oshirish
    asyncio.create_task(
        _safe_save_message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response,
            message_type="text",
        )
    )
    asyncio.create_task(_safe_increment_daily_usage(user))
    asyncio.create_task(_safe_update_relationship(user, ai_profile, user_text, bot))

    logger.info(
        "Javob yuborildi: user_id={}, conversation_id={}, len={}",
        user.id,
        conversation.id,
        len(full_response),
    )
