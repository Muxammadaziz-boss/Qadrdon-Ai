"""Qadirdon AI — Uzoq Muddatli Faktlar Xotirasi (Long-Term Memory Extractor).

Foydalanuvchi suhbat davomida aytgan muhim ma'lumotlarini (ismi, kasbi,
shahri, yoqtirgan narsalari, rejalari) avtomatik ajratib olib xotirada saqlash.
"""

from __future__ import annotations

import re
from typing import Any
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserFact
from db.session import async_session

# O'zbek tilidagi muntazam iboralar (Tezkor va aniq qoidalar)
NAME_PATTERNS = [
    re.compile(r"(?:mening\s+)?ismim\s+([A-ZА-ЯЁa-zа-яёʻʼ'\-]+)", re.IGNORECASE),
    re.compile(r"meni\s+([A-ZА-ЯЁa-zа-яёʻʼ'\-]+)\s+deng", re.IGNORECASE),
    re.compile(r"o'zimni\s+ismim\s+([A-ZА-ЯЁa-zа-яёʻʼ'\-]+)", re.IGNORECASE),
]

JOB_PATTERNS = [
    re.compile(r"\b(dasturchi|o['ʻʼ]qituvchi|shifokor|doktor|talaba|student|haydovchi|tadbirkor|biznesmen|injener|usta|buxgalter|oshpaz|menejer|dizayner|marketolog)man\b", re.IGNORECASE),
    re.compile(r"kasbim\s+([A-ZА-ЯЁa-zа-яёʻʼ'\-\s]{3,30})", re.IGNORECASE),
    re.compile(r"soham\s+([A-ZА-ЯЁa-zа-яёʻʼ'\-\s]{3,30})", re.IGNORECASE),
]

CITY_PATTERNS = [
    re.compile(r"\b(toshkent|samarqand|buxoro|andijon|farg['ʻʼ]ona|namangan|qashqadaryo|surxondaryo|xorazm|jizzax|sirdaryo|navoiy|nukus|rossiya|turkiya|koreya|dubay|amerika)(?:da|dan|ga)\s+(?:yashayman|turaman|keldim|yuribman)", re.IGNORECASE),
    re.compile(r"shahrim\s+([A-ZА-ЯЁa-zа-яёʻʼ'\-]+)", re.IGNORECASE),
]

PREFERENCE_PATTERNS = [
    re.compile(r"sevimli\s+taomim\s+([A-ZА-ЯЁa-zа-яёʻʼ'\-\s]{3,30})", re.IGNORECASE),
    re.compile(r"([A-ZА-ЯЁa-zа-яёʻʼ'\-\s]{3,20})(?:ni|i)\s+juda\s+yaxshi\s+ko['ʻʼ]raman", re.IGNORECASE),
    re.compile(r"menga\s+([A-ZА-ЯЁa-zа-яёʻʼ'\-\s]{3,20})\s+yoqadi", re.IGNORECASE),
]

PLAN_PATTERNS = [
    re.compile(r"\b(ertaga\s+[^.!?\n]{5,40})", re.IGNORECASE),
    re.compile(r"\b(shanba\s+kuni\s+[^.!?\n]{5,40})", re.IGNORECASE),
    re.compile(r"\b(yakshanba\s+kuni\s+[^.!?\n]{5,40})", re.IGNORECASE),
    re.compile(r"\b(keyingi\s+hafta\s+[^.!?\n]{5,40})", re.IGNORECASE),
]


def extract_facts_from_text(text: str) -> list[dict[str, str]]:
    """Matndan foydalanuvchi shaxsiy faktlarini ajratib oladi."""
    facts = []

    # 1. Ism
    for pat in NAME_PATTERNS:
        match = pat.search(text)
        if match:
            name = match.group(1).strip().title()
            if len(name) >= 2:
                facts.append({"category": "name", "fact_key": "Ismi", "fact_value": name})
                break

    # 2. Kasb
    for pat in JOB_PATTERNS:
        match = pat.search(text)
        if match:
            job = match.group(1).strip().capitalize()
            facts.append({"category": "job", "fact_key": "Kasbi/Mashg'uloti", "fact_value": job})
            break

    # 3. Shahar
    for pat in CITY_PATTERNS:
        match = pat.search(text)
        if match:
            city = match.group(1).strip().title()
            facts.append({"category": "city", "fact_key": "Yashash joyi", "fact_value": city})
            break

    # 4. Qiziqish / Taom
    for pat in PREFERENCE_PATTERNS:
        match = pat.search(text)
        if match:
            pref = match.group(1).strip().capitalize()
            facts.append({"category": "preference", "fact_key": "Yoqtirgan narsasi/taomi", "fact_value": pref})
            break

    # 5. Reja
    for pat in PLAN_PATTERNS:
        match = pat.search(text)
        if match:
            plan = match.group(1).strip()
            facts.append({"category": "plan", "fact_key": "Yaqin rejalari", "fact_value": plan})
            break

    return facts


async def save_extracted_facts(
    user_id: int,
    conversation_id: int | None,
    facts: list[dict[str, str]],
) -> int:
    """Ajratilgan faktlarni bazaga kiritadi yoki yangilaydi."""
    if not facts:
        return 0

    saved_count = 0
    async with async_session() as session:
        for item in facts:
            # Mavjud fakt bormi?
            stmt = select(UserFact).where(
                UserFact.user_id == user_id,
                UserFact.fact_key == item["fact_key"],
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                existing.fact_value = item["fact_value"]
                existing.category = item["category"]
            else:
                new_fact = UserFact(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    category=item["category"],
                    fact_key=item["fact_key"],
                    fact_value=item["fact_value"],
                )
                session.add(new_fact)
            saved_count += 1

        await session.commit()
    return saved_count


async def get_user_facts_prompt(user_id: int) -> str:
    """Foydalanuvchining barcha saqlangan faktlarini tizim prompti uchun matn shaklida oladi."""
    async with async_session() as session:
        stmt = (
            select(UserFact)
            .where(UserFact.user_id == user_id)
            .order_by(UserFact.updated_at.desc())
            .limit(10)
        )
        result = await session.execute(stmt)
        facts = result.scalars().all()

    if not facts:
        return ""

    lines = ["\nFOYDALANUVCHI HAQIDA BILGANLARINGIZ (Uzoq muddatli xotira):"]
    for f in facts:
        lines.append(f"- {f.fact_key}: {f.fact_value}")
    lines.append("⚠️ KO'RSATMA: Ushbu ma'lumotlarni suhbat davomida tabiiy, insoniy tarzda eslab tur!")
    return "\n".join(lines)
