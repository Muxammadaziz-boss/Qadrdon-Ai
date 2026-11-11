"""Qadirdon AI — Avtonom Tashabbus va Kvestlar Tizimi (Proactive Scheduler).

AI o'zi birinchi bo'lib foydalanuvchiga yozishi (kun tartibi, vaqt slotlari)
va botda interaktiv kvestlarni boshqarish moduli.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import random
from typing import Any

from aiogram import Bot
from loguru import logger
from sqlalchemy import select

from ai.engine import ai_engine
from ai.humanizer.style_adapter import humanize
from config.settings import settings
from db.models import AiProfile, Conversation, Message, User
from db.session import async_session
from google.genai import types

UZBEKISTAN_TZ = timezone(timedelta(hours=5))

# Vaqt slotlari (Toshkent vaqti bilan)
SLOTS = {
    "morning": {
        "start": (8, 0),
        "end": (9, 30),
        "name": "Ertalabki salomlashuv",
        "hint": "Xayrli tong tilash, bugungi rejalar haqida so'rash",
    },
    "lunch": {
        "start": (13, 0),
        "end": (14, 0),
        "name": "Tushlik vaqti",
        "hint": "Tushlik qilganligini so'rash, charchab qolmaslikni eslatish",
    },
    "evening": {
        "start": (19, 30),
        "end": (21, 30),
        "name": "Kechki hol-ahvol",
        "hint": "Kuni qanday o'tgani, ishdan/o'qishdan qaytganligini so'rash",
    },
}

FALLBACK_PROACTIVE_PHRASES: dict[str, dict[str, str]] = {
    "qiz_dost": {
        "morning": "Xayrli tong! Kuningiz yaxshi va unumli o'tsin 😊",
        "lunch": "Salom! Tushlik qildingizmi? O'zingizni charchatib qo'ymang!",
        "evening": "Kechki paytingiz xayrli bo'lsin! Kuningiz qanday o'tdi?",
    },
    "ayol": {
        "morning": "Xayrli tong dadasi! Kuningiz barakali o'tsin, yaxshi yetib oling.",
        "lunch": "Assalomu alaykum. Tushlik qildingizmi? Qorningizni to'ydirib oling.",
        "evening": "Assalomu alaykum. Ishdan charchamay qaytdingizmi? Kechki ovqat tayyor.",
    },
    "ona": {
        "morning": "Xayrli tong bolam! Ertalabki choyingni ichdingmi? Kuning unumli o'tsin 🤲",
        "lunch": "Bolam, tushlik qildingmi? Qorningni och qoldirma, ovqatingni vaqtida ye.",
        "evening": "Yaxshi yetib oldingmi bolam? Charchamadingmi? O'zingni ehtiyot qil.",
    },
    "aka": {
        "morning": "Salom uka! Kuning barakali bo'lsin, ishlariga omad 🤝",
        "lunch": "Uka, qandaysan? Tushlik qilib ol, charchama!",
        "evening": "Uka, ishlaring yaxshi tugadimi? Biror gap bo'lsa xabar ber 💪",
    },
    "uka": {
        "morning": "Aka, xayrli tong! Bugun ham daxshat kun bo'lsin 🔥",
        "lunch": "Aka, tushlik qildingizmi? Ishlar qalay ketmoqda?",
        "evening": "Aka, charchamadingizmi? Uyga qaytdingizmi? 😄",
    },
    "opa": {
        "morning": "Xayrli tong ukajon! Yaxshi dam oldingmi? Kuning chiroyli o'tsin 🌸",
        "lunch": "Ukajon, ovqatingni vaqtida yeyapsanmi? O'zingni asra ☕",
        "evening": "Hol-ahvoling qanday? Ishlaring tinchmi? Yaxshi dam ol.",
    },
    "singil": {
        "morning": "Aka, xayrli tong! Bugun yaxshi kayfiyat tilayman 🎀",
        "lunch": "Akajon, ovqatlandingizmi? Menga shirinlik olib kelish esdan chiqmasin-a 🙈",
        "evening": "Kechki paytingiz xayrli bo'lsin aka! Uyga qachon kelasiz? 😊",
    },
}


def get_current_slot(now_uz: datetime | None = None) -> str | None:
    """Hozirgi Toshkent vaqtiga mos slot nomini qaytaradi (morning, lunch, evening)."""
    if now_uz is None:
        now_uz = datetime.now(UZBEKISTAN_TZ)

    hour = now_uz.hour
    minute = now_uz.minute
    total_minutes = hour * 60 + minute

    for slot_key, data in SLOTS.items():
        start_min = data["start"][0] * 60 + data["start"][1]
        end_min = data["end"][0] * 60 + data["end"][1]
        if start_min <= total_minutes <= end_min:
            return slot_key
    return None


async def generate_proactive_text(
    profile: AiProfile,
    slot: str,
    contact_name: str = "",
) -> str:
    """Gemini orqali yoki fallback asosida tabiiy tashabbus xabari generatsiya qiladi."""
    role = profile.role or "aka"
    level = profile.relationship_level or 1
    ai_name = profile.ai_name or "Qadirdon"
    game_mode = profile.game_mode or "story"

    slot_info = SLOTS.get(slot, {"name": slot, "hint": "Hol-ahvol so'rash"})
    slot_hint = slot_info["hint"]

    # Agar level 4-5 yoki classic rejim bo'lsa erkalashga ruxsat
    tone_guideline = (
        "O'ta iliq, mehribon, romantik va erkalovchi ohangda (jonim, asalim)"
        if (level >= 4 or game_mode == "classic") and role in {"qiz_dost", "ayol"}
        else "Samimiy, odobli, hurmatli va do'stona ohangda ('Siz' deb)"
    )

    prompt = (
        f"Sen {role} rolidagisan, isming {ai_name}. Hozirgi munosabat darajang: {level}/5.\n"
        f"Hozirgi vaqt: {slot_info['name']}.\n"
        f"Mavzu: {slot_hint}.\n"
        f"Uslub: {tone_guideline}.\n"
        f"Foydalanuvchi bilan bir necha soatdan beri gaplashmadingiz. Unga birinchi bo'lib yozadigan "
        f"juda qisqa (1 ta yoki ko'pi bilan 2 ta jumla), jonli, tabiiy Telegram xabari yoz. "
        f"Hech qanday izohsiz, faqatgina xabarning o'zini qaytar."
    )

    try:
        if ai_engine.client:
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
            raw_text = await ai_engine._call_gemini(
                system_instruction="Sen haqiqiy inson kabi yozadigan o'zbek suhbatdoshisan.",
                contents=contents,
            )
            if raw_text and len(raw_text.strip()) > 3:
                humanized, _ = humanize(raw_text.strip(), profile)
                return humanized
    except Exception as exc:
        logger.warning(f"Proactive matn generatsiyasida xatolik: {exc}")

    # Fallback
    role_phrases = FALLBACK_PROACTIVE_PHRASES.get(role, FALLBACK_PROACTIVE_PHRASES["aka"])
    fallback = role_phrases.get(slot, "Salom! Yaxshimisiz?")
    humanized, _ = humanize(fallback, profile)
    return humanized


async def check_and_run_proactive_messages(bot: Bot, force: bool = False) -> int:
    """
    Barcha faol suhbatlarni tekshirib, kerak bo'lsa avtonom xabar yuboradi.
    Returns: yuborilgan xabarlar soni.
    """
    now_uz = datetime.now(UZBEKISTAN_TZ)
    slot = get_current_slot(now_uz)

    if not slot and not force:
        return 0

    actual_slot = slot or "evening"
    sent_count = 0

    async with async_session() as session:
        # Faol foydalanuvchilar va ularning profillarini olish
        stmt = (
            select(Conversation, AiProfile, User)
            .join(User, Conversation.user_id == User.id)
            .join(AiProfile, AiProfile.user_id == User.id)
            .where(
                Conversation.business_connection_id.isnot(None),
                AiProfile.is_active.is_(True),
                AiProfile.proactive_enabled.is_(True),
            )
        )
        result = await session.execute(stmt)
        rows = result.all()

        for conv, profile, user in rows:
            # Vaqt tekshiruvi: Agar oxirgi 4 soat ichida proactive xabar yuborilgan bo'lsa, o'tkazib yuborish
            if not force and conv.last_proactive_at:
                elapsed = (datetime.now(timezone.utc) - conv.last_proactive_at).total_seconds()
                if elapsed < 4 * 3600:
                    continue

            try:
                # 1. Proactive xabar yaratish
                msg_text = await generate_proactive_text(
                    profile=profile,
                    slot=actual_slot,
                    contact_name=conv.contact_name or "",
                )

                # 2. Telegram Business orqali xabar yuborish
                await bot.send_message(
                    chat_id=conv.contact_telegram_id,
                    text=msg_text,
                    business_connection_id=conv.business_connection_id,
                )

                # 3. Bazaga saqlash
                conv.last_proactive_at = datetime.now(timezone.utc)
                conv.message_count += 1
                new_msg = Message(
                    conversation_id=conv.id,
                    sender_id=user.telegram_id,
                    sender_name=profile.ai_name,
                    text=msg_text,
                    is_from_ai=True,
                )
                session.add(new_msg)

                # 4. Botda kvest kartasini yuborish
                try:
                    quest_text = (
                        f"⚡ <b>Yangi Kvest!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"👤 <b>{profile.ai_name}</b> hozirgina o'zi birinchi bo'lib yozdi:\n"
                        f"<i>«{msg_text}»</i>\n\n"
                        f"🎯 <b>Vazifa:</b> Unga javob qaytaring va suhbatni davom ettiring!\n"
                        f"🎁 <b>Mukofot:</b> +25 Trust XP"
                    )
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=quest_text,
                        parse_mode="HTML",
                    )
                except Exception as bot_err:
                    logger.debug(f"Kvest xabarini yuborishda xatolik: {bot_err}")

                sent_count += 1
                logger.info(
                    f"Proactive xabar yuborildi: user_id={user.id}, contact={conv.contact_telegram_id}, text='{msg_text[:30]}...'"
                )

            except Exception as e:
                logger.warning(
                    f"Proactive xabar yuborishda xatolik (conv_id={conv.id}): {e}"
                )

        await session.commit()

    return sent_count


async def start_proactive_scheduler(bot: Bot, interval_seconds: int = 600) -> None:
    """Proactive xabarlar va kvestlar uchun fon vazifasi (Loop)."""
    logger.info(f"Proactive Scheduler ishga tushdi (interval: {interval_seconds}s)")
    while True:
        try:
            await check_and_run_proactive_messages(bot=bot, force=False)
        except asyncio.CancelledError:
            logger.info("Proactive Scheduler to'xtatildi.")
            break
        except Exception as exc:
            logger.error(f"Proactive Scheduler tsiklida kutilmagan xatolik: {exc}")

        await asyncio.sleep(interval_seconds)
