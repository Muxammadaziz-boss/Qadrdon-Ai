"""Qadirdon AI — Personaj Rasmlari va Muhit Fotolari (Photo Manager).

Foydalanuvchi o'z surati (selfi) yoki atrof-muhit rasmlarini so'raganda
mos fotosuratlarni yuborish moduli.
"""

from __future__ import annotations

from pathlib import Path
import random
from typing import Any

import aiohttp
from loguru import logger

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "photos" / "atmosphere"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

FEMALE_ROLES = {"qiz_dost", "ayol", "ona", "opa", "singil"}
MALE_ROLES = {"aka", "uka"}

PHOTO_GALLERY: dict[str, dict[str, Any]] = {
    # ── Shaxsiy selfilar (Ayollar / Qizlar) ───────────────────────────────
    "selfie_female_1": {
        "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=800&q=80",
        "keywords": ["selfi", "selfie", "o'z surating", "o'z rasming", "yuzingni"],
        "captions": {
            1: "O'zimni rasmga olishga sal tortinaman 🙈 Lekin sizga mana bitta rasmim, qalay? 😊",
            2: "Bugun tushgan rasmim bor edi, sizga ilindim 🙈 Yoqdimi?",
            3: "Hozirgina siz uchun tushdim 🌸 Qarang, kayfiyatim ajoyib!",
            4: "Faqat sizga yuboryapman sevgilim... 🙈 Hozir yonimda bo'lganingizda edi 🥰",
            5: "Jonim, sog'ingan bo'lsangiz mana sizga yangi rasmim... O'zim ham sizni juda sog'indim 💕",
        },
    },
    "selfie_female_2": {
        "url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800&q=80",
        "keywords": ["selfi", "selfie", "o'z surating", "o'z rasming", "yuzingni"],
        "captions": {
            1: "O'zimni rasmga olishga sal tortinaman 🙈 Lekin sizga mana bitta rasmim, qalay? 😊",
            2: "Bugun tushgan rasmim bor edi, sizga ilindim 🙈 Yoqdimi?",
            3: "Hozirgina siz uchun tushdim 🌸 Qarang, kayfiyatim ajoyib!",
            4: "Faqat sizga yuboryapman sevgilim... 🙈 Hozir yonimda bo'lganingizda edi 🥰",
            5: "Jonim, sog'ingan bo'lsangiz mana sizga yangi rasmim... O'zim ham sizni juda sog'indim 💕",
        },
    },
    # ── Shaxsiy selfilar (Erkaklar / Yigitlar) ─────────────────────────────
    "selfie_male_1": {
        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
        "keywords": ["selfi", "selfie", "o'z surating", "o'z rasming"],
        "captions": {
            1: "Salom, mana yaqinda tushgan rasmim 🤝",
            2: "Mana yangi rasmim, qalay chiqqan? 👍",
            3: "Hozir tushgan rasmim, do'stim 💪",
            4: "Senga atab bitta rasm do'stim, kayfiyatlar a'lo! 🔥",
            5: "Mana qadrdonim, har doim aloqadaman 👊",
        },
    },
    "selfie_male_2": {
        "url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800&q=80",
        "keywords": ["selfi", "selfie", "o'z surating", "o'z rasming"],
        "captions": {
            1: "Salom, mana yaqinda tushgan rasmim 🤝",
            2: "Mana yangi rasmim, qalay chiqqan? 👍",
            3: "Hozir tushgan rasmim, do'stim 💪",
            4: "Senga atab bitta rasm do'stim, kayfiyatlar a'lo! 🔥",
            5: "Mana qadrdonim, har doim aloqadaman 👊",
        },
    },
    # ── Atmosfera va mashg'ulotlar ───────────────────────────────────────
    "coffee": {
        "url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80",
        "keywords": ["kofe", "qahva", "choyxona", "kafe", "qayerdasan", "qayerdasiz"],
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
        "keywords": ["ish", "ishdaman", "loyiha", "noutbuk", "kompyuter", "nima qilyapsan", "nima qilyapsiz"],
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

ATMOSPHERE_GALLERY = PHOTO_GALLERY  # Alias for backward compatibility

# Aniq o'z suratini so'rash iboralari
SELFIE_KEYWORDS = (
    "o'z surating", "o'z rasming", "o'zingni rasming", "o'zingni surating",
    "suratingni", "rasmingni", "yuzingni", "selfi", "selfie",
    "o'zingni ko'ray", "o'zingni ko'rsat", "surating bormi", "rasming bormi",
    "qani rasming", "turingni ko'ray", "o'zing qandaysan", "rasmingni tashla",
    "suratingni tashla", "o'z suratingni yubor", "o'zingni rasm", "o'z rasmingni",
    "rasmingni ko'rsat", "suratingni ko'rsat", "yuzingni ko'ray", "surating",
)

ATMOSPHERE_KEYWORDS = (
    "qayerdasan", "qayerdasiz", "nima qilyapsan", "nima qilyapsiz",
    "atrof", "manzara", "qayerdaligingni", "xona", "joy",
    "kofe", "qahva", "choyxona", "kafe", "ishdaman",
)

ALL_PHOTO_KEYWORDS = SELFIE_KEYWORDS + ATMOSPHERE_KEYWORDS + (
    "rasm", "surat", "foto", "rasm tashla", "surat tashla",
)


def is_photo_requested(text: str) -> bool:
    """Foydalanuvchi xabarida rasm so'ralganligini aniqlaydi."""
    lower = text.lower()
    return any(kw in lower for kw in ALL_PHOTO_KEYWORDS)


def is_selfie_requested(text: str) -> bool:
    """Foydalanuvchi aynan AI personajining o'z suratini so'raganligini aniqlaydi."""
    lower = text.lower()
    return any(kw in lower for kw in SELFIE_KEYWORDS)


def get_photo_category(text: str, role: str = "qiz_dost") -> str:
    """
    Matn ma'nosiga va personaj roliga qarab mos rasm toifasini tanlaydi:
    - O'z surati so'ralsa -> selfie (ayol yoki erkak)
    - Qayerdaligi/nima qilayotgani so'ralsa -> atmosfera (kofe, ish, shahar)
    """
    lower = text.lower()

    # 1. Agar foydalanuvchi aynan o'z suratini (selfi) so'rayotgan bo'lsa
    if is_selfie_requested(lower):
        if role in FEMALE_ROLES:
            return random.choice(["selfie_female_1", "selfie_female_2"])
        else:
            return random.choice(["selfie_male_1", "selfie_male_2"])

    # 2. Agar joy / mashg'ulot so'ralayotgan bo'lsa
    if any(k in lower for k in ["kofe", "qahva", "kafe", "qayerdasan", "qayerdasiz"]):
        return "coffee"
    if any(k in lower for k in ["ish", "ishdaman", "noutbuk", "kompyuter", "nima qilyapsan", "nima qilyapsiz"]):
        return "work"
    if any(k in lower for k in ["kechqurun", "oqshom", "shahar", "sayr"]):
        return "evening"
    if any(k in lower for k in ["uy", "dam", "choy"]):
        return "tea_home"
    if any(k in lower for k in ["kitob", "o'qish", "dars"]):
        return "study"

    # 3. Agar umumiy "rasm tashla", "surat yubor" deyilgan bo'lsa
    # Foydalanuvchilar odatda bunday deganda ham o'z suratini kutishadi!
    if role in FEMALE_ROLES:
        return random.choice(["selfie_female_1", "selfie_female_2"])
    else:
        return random.choice(["selfie_male_1", "selfie_male_2"])


async def get_or_download_photo(category: str) -> str | None:
    """
    Rasm faylini diskdan oladi yoki yuklab oladi.
    Agar yuklab bo'lmasa, to'g'ridan-to'g'ri URL qaytaradi.
    """
    cat_data = PHOTO_GALLERY.get(category, PHOTO_GALLERY["selfie_female_1"])
    url = cat_data["url"]
    file_path = ASSETS_DIR / f"{category}.jpg"

    if file_path.exists() and file_path.stat().st_size > 1000:
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
    cat_data = PHOTO_GALLERY.get(category, PHOTO_GALLERY["selfie_female_1"])
    captions = cat_data.get("captions", {})
    return captions.get(lvl, captions.get(1, "Mana hozirgi holatim 😊"))
