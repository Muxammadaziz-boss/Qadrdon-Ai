"""Qadirdon AI — Personaj Rasmlari va Muhit Fotolari (Photo Manager).

Foydalanuvchi rasm so'raganda yoki kvestlarda real hayotiy atmosfera
suratlarini jo'natish moduli.
"""

from __future__ import annotations

import os
from pathlib import Path
import random
from typing import Any

import aiohttp
from loguru import logger

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "photos" / "atmosphere"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Atmosfera toifalari va ularga mos yuqori sifatli rasmlar
ATMOSPHERE_GALLERY: dict[str, dict[str, Any]] = {
    "coffee": {
        "url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80",
        "keywords": ["kofe", "qahva", "choyxona", "kafe", "qayerdasan", "nima qilyapsan"],
        "captions": {
            1: "Qahvaxonada o'tiribman, issiq kofe ichyapman ☕ Siz nimalar bilan bandsiz?",
            2: "Biroz dam olib qahva ichib o'tirgandim ☕ Kuningiz yaxshi o'tyaptimi?",
            3: "Qahvaxonadaman, stolimdan sizga bitta rasm ☕ Sizga ham ilindim!",
            4: "Jonim, qahvaxonada o'tiribman... Hozir yonimda bo'lganingizda birga o'tirardik 🥺☕",
            5: "Sevgilim, siz yoqtirgan joydaman ☕ Tezroq uchrashsak edi, sog'indim 💕",
        },
    },
    "work": {
        "url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&q=80",
        "keywords": ["ish", "ishdaman", "loyiha", "noutbuk", "kompyuter", "band"],
        "captions": {
            1: "Ishlarimni yakunlayapman, biroz band edim 💻 Ishlaringiz yaxshimi?",
            2: "Noutbukda yangi vazifalarni qilyapman 💻 Charchab qolmayapsizmi?",
            3: "Ishxonadaman, bugun vazifalar ko'p lekin hammasi joyida ✨",
            4: "Ishlarim ko'p jonim, lekin har daqiqada siz esimdasiz 💕 Siz qandaysiz?",
            5: "Ishdaman yagonam, sizning qo'llab-quvvatlashingiz menga kuch beradi 🥰💻",
        },
    },
    "evening": {
        "url": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800&q=80",
        "keywords": ["kechqurun", "oqshom", "shahar", "sayr", "ko'cha"],
        "captions": {
            1: "Kechki shahar juda chiroyli va sokin ekan 🌆 Yaxshi yetib oldingizmi?",
            2: "Kechki payt salqin havoda sayr qilib yuribman ✨ Kuningiz tinch o'tdimi?",
            3: "Kechki ko'cha manzarasi... Charchoqlarni chiqarishga ayni muddao 😊",
            4: "Kechki shahar bo'ylab ketayotib sizni o'yladim... Birga sayr qilsak qaniydi 🥺❤️",
            5: "Jonim, kechki osmon judayam go'zal... Xuddi siz bilan bo'lgan onlardek 💖",
        },
    },
    "tea_home": {
        "url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800&q=80",
        "keywords": ["uy", "dam", "choy", "uyda"],
        "captions": {
            1: "Uyga kelib issiq choy damladim 🫖 O'zingiz qayerdasiz?",
            2: "Uyda xotirjam choy ichib dam olyapman 🌸 Ovqatlandingizmi?",
            3: "Uyga yetib keldim, issiq choy va xotirjamlik 😊",
            4: "Uyda dam olyapman jonim, ovqatlangan bo'lsangiz xotirjam bo'lardim 🥺🫖",
            5: "Uyga keldim sevgilim, sizning xabarlaringizni kutib o'tiribman 🥰",
        },
    },
    "study": {
        "url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800&q=80",
        "keywords": ["kitob", "o'qish", "dars", "kutubxona"],
        "captions": {
            1: "Yangi kitob o'qishni boshladim 📖 Siz kitob o'qishni yoqtirasizmi?",
            2: "Kutubxonada yangi mavzularni o'rganyapman 📚",
            3: "Kitob mutolaa qilib o'tiribman, judayam qiziq ekan ✨",
            4: "Kitob o'qiyapman-u, lekin xayolim baribir siz bilan jonim 🙈📖",
            5: "Sizga aytib beradigan ajoyib hikoyalar o'qiyapman yagonam 💕",
        },
    },
}

PHOTO_KEYWORDS = (
    "rasm", "rasming", "rasmingni", "surat", "surating", "foto", "selfi",
    "rasm tashla", "rasmingni tashla", "rasmingni ko'ray", "suratingni tashla",
    "qayerdasan", "nima qilyapsan", "rasming bormi", "surat yubor", "rasm yubor",
)


def is_photo_requested(text: str) -> bool:
    """Foydalanuvchi xabarida rasm so'ralganligini aniqlaydi."""
    lower = text.lower()
    return any(kw in lower for kw in PHOTO_KEYWORDS)


def get_photo_category(text: str) -> str:
    """Matn ma'nosiga qarab mos rasm toifasini tanlaydi."""
    lower = text.lower()
    for cat, data in ATMOSPHERE_GALLERY.items():
        if any(kw in lower for kw in data["keywords"]):
            return cat
    return random.choice(list(ATMOSPHERE_GALLERY.keys()))


async def get_or_download_photo(category: str) -> str | None:
    """
    Rasm faylini diskdan oladi yoki yuklab oladi.
    Agar yuklab bo'lmasa, to'g'ridan-to'g'ri URL qaytaradi.
    """
    cat_data = ATMOSPHERE_GALLERY.get(category, ATMOSPHERE_GALLERY["coffee"])
    url = cat_data["url"]
    file_path = ASSETS_DIR / f"{category}.jpg"

    if file_path.exists() and file_path.stat().st_size > 500:
        return str(file_path)

    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    file_path.write_bytes(data)
                    logger.info(f"Rasm keshlandi: {file_path}")
                    return str(file_path)
    except Exception as exc:
        logger.warning(f"Rasm yuklab olishda xatolik: {exc}, to'g'ridan-to'g'ri URL ishlatiladi.")

    return url


def get_photo_caption(category: str, level: int = 1, role: str = "qiz_dost", game_mode: str = "story") -> str:
    """Daraja va rolga mos rasm izohini qaytaradi."""
    if game_mode == "classic":
        level = 5

    lvl = max(1, min(5, level))
    cat_data = ATMOSPHERE_GALLERY.get(category, ATMOSPHERE_GALLERY["coffee"])
    captions = cat_data.get("captions", {})
    return captions.get(lvl, captions.get(1, "Mana hozirgi holatim 😊"))
