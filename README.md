# 🤖 Qadirdon AI — Telegram Business orqali Shaxsiy Profildan Muloqot Qiluvchi Sun'iy Intellekt

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.15%2B-blueviolet?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![Gemini AI](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-orange?logo=google&logoColor=white)](https://ai.google.dev/)
[![Telegram Business](https://img.shields.io/badge/Telegram-Business%20API-2CA5E0?logo=telegram&logoColor=white)](https://core.telegram.org/bots/api#business)
[![Tests](https://img.shields.io/badge/Tests-35%20Passed-brightgreen)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Telegram Business API orqali shaxsiy profilingiz nomidan xuddi haqiqiy insondek yozadigan va foydalanuvchi tanloviga ko'ra — aka, uka, opa, singil, ona, qiz do'st yoki suyukli rafiqa bo'lib muloqot qiluvchi innovatsion sun'iy intellekt tizimi.**

[Personajlar Katalogi (42 ta model)](CHARACTERS.md) • [Hissa Qo'shish](CONTRIBUTING.md) • [Litsenziya](LICENSE)

</div>

---

## 🌟 Asosiy Imkoniyatlar va Afzalliklar

### 1. 📱 Yagona Bot Konsepsiyasi (All-in-One Bot)
- **Faqat bitta bot orqali:** Foydalanuvchi sozlamalari, personaj tanlash, munosabat taraqqiyoti, Telegram Business ulanishi va Administrator kabineti boshqariladi.
- Bot shaxsiy chatda xizmat va sozlamalar paneli sifatida xizmat qiladi, asosiy jonli muloqot esa foydalanuvchining shaxsiy Telegram profili orqali kechadi.

### 2. 🎭 7 ta Rol va 42 ta Real O'zbek Hayotiy Personajlari
Tizimda har bir rol uchun 6 tadan, jami **42 ta boy hayotiy personaj modellari** mavjud:
- 👰 **Ayol / Turmush o'rtog'i** (Zarina, Nodira, Gulnoza, Shaxnoza, Munisa, Feruza) — ro'zg'or, oila bekasi, issiq mehr va sadoqat.
- 🤱 **Ona** (Fotima opa, Mastura xola, Dilbar opa, Halima buvijon, Ziyoda opa, Gulchehra opa) — cheksiz duo, mehr, g'amxo'rlik.
- 👨 **Aka** (Sardor, Jasur, Bobur, Mansur, Ulug'bek, Bekzod) — himoyachi, suyanchiq, erkakcha maslahatlar.
- 👦 **Uka** (Shohrux, Azizbek, Bilol, Davron, Otabek, Samandar) — quvnoq, samimiy, akasiga suyanuvchi.
- 👩 **Opa** (Shahodat opa, Nargiza opa, Zulayho opa, Mohira opa, Dildora opa, Malika opa) — g'amxo'r, sirdosh, dardkash.
- 👧 **Singil** (Madinabonu, Sabina, Yulduz, Gulbahor, Diyora, Nozima) — erka, mehrli, yoqimtoy.
- 💕 **Qiz do'st** (Rayhona, Kamola, Madina, Sevinch, Mohira, Dildora) — romantik, samimiy, nozik qalbli.

> Barcha personajlarning to'liq tarixi, sirlari va kasblari bilan [CHARACTERS.md](CHARACTERS.md) hujjatida tanishing.

### 3. 🕹️ Ikki Xil Muloqot Rejimi (Game Modes)
- 🎮 **Zabt etish (Story rejim):**
  - Munosabat 1-bosqichdan ("Siz", begona va rasmiy) boshlanadi.
  - Suhbatlar va javoblar orqali **Ishonch (XP)** yig'iladi va munosabat darajasi 1 dan 5-bosqichgacha ko'tariladi.
  - Har bir daraja oshganda personaj o'zining shaxsiy sirlarini ochadi va yangi kvestlar paydo bo'ladi.
- 🌟 **Klassik rejim:**
  - Sinovlarsiz, boshidanoq 5-darajadagi yaqinlik va erkinlik.
  - Hech qanday cheklovlarsiz to'liq erkalash va sirdoshona suhbat.

### 4. 🧠 Insondek Yozish Texnologiyasi (Humanizer Engine)
- **Typing Simulation**: Matn uzunligiga qarab Telegramda haqiqiy *"yozmoqda..."* holatini ushlab turadi.
- **Xabarlarni bo'laklash**: Insonlarga o'xshab uzun gaplarni birdan emas, 2-3 ta qisqa xabar qilib jo'natadi.
- **Tabiiy xatolar (Typo Engine)**: Ba'zida shoshganda harf adashib ketib, keyin `*tuzatish` orqali to'g'rilab yozadi.
- **Jonli Slang & O'zbekona Iboralar**: `"rahmat"` o'rniga `"raxmat"`, `"ho'p bo'ladi"`, `"gap yo'q"` kabi xalqona chat tili.

### 5. 🔊 Aqlli Ovoz Tizimi (Smart Voice Filtering)
- Tanlangan personajning jinsiga mos holda faqat mos ovozlar (ayollar uchun ayol ovozlari, erkaklar uchun erkak ovozlari) taqdim etiladi.
- Google Cloud Text-to-Speech va Speech-to-Text integratsiyasi.
- Telegram VoIP (Pyrogram + pytgcalls) orqali ovozli qo'ng'iroqlarni qabul qilish arxitekturasi.

### 6. 💰 Balans va Obunalar Tizimi
- Har bir foydalanuvchining shaxsiy ichki balansi.
- Karta orqali to'lov va admin orqali bir zumda balansni to'ldirish.
- 3 xil tarif rejasi: **Standard**, **Premium** va **Ultra VIP**.

### 7. 🔐 Admin Boshqaruv Paneli (`/admin`)
- 📊 **Statistika**: Jami foydalanuvchilar, faol AI profillar, obunalar va umumiy balans.
- 💳 **Balans to'ldirish**: Foydalanuvchi ID raqamiga to'g'ridan-to'g'ri pul qo'shish yoki ayirish.
- 💎 **Obuna berish**: ID bo'yicha tezkor obuna sovg'a qilish.
- 🔍 **Foydalanuvchi qidiruvi**: Shaxsiy ma'lumotlar, chat tarixi va faollik tahlili.
- 📢 **Broadcast**: Barcha foydalanuvchilarga e'lon xabarini yuborish.

---

## 🏗️ Arxitektura va Texnologiyalar

```
Qadirdon-Ai/
├── ai/                      # Sun'iy intellekt moduli (Google Gemini 2.0 Flash)
│   ├── characters/          # 7 ta rol bo'yicha 42 ta o'zbek personaj modellari
│   ├── humanizer/           # Typo, slang, emoji va uslub simulatorlari
│   ├── memory/              # Qisqa va uzoq muddatli xotira tizimi
│   ├── prompts/             # Munosabat darajalari (1-5) va tizim ko'rsatmalari
│   ├── quests/              # Kvestlar boshqaruvi
│   └── engine.py            # Asosiy AI dvigateli
├── bot/                     # Aiogram 3 asosidagi foydalanuvchi boti & Admin kabineti
│   ├── handlers/            # /start, sozlash, balans, tariflar, admin boshqaruvi
│   ├── keyboards/           # Inline va reply klaviaturalar
│   ├── middlewares/         # Autentifikatsiya, foydalanuvchi kesh va DB sessiyasi
│   └── states/              # FSM holatlari (sozlash va admin)
├── business/                # Telegram Business API moduli
│   ├── handlers/            # Shaxsiy profildan yoziladigan xabarlarni tutuvchi handlerlar
│   └── utils/               # Jonli kechikish va yozish simulatori
├── config/                  # Pydantic v2 asosidagi markaziy konfiguratsiya
├── db/                      # SQLAlchemy 2.0 (Async) + aiosqlite / PostgreSQL
├── tests/                   # Pytest asosidagi unit va integratsion testlar
├── utils/                   # Loguru logger va yordamchi funksiyalar
├── voice/                   # Ovoz profillari, TTS, STT va VoIP
└── run.py                   # Yagona botni ishga tushiruvchi kirish nuqtasi
```

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Repozitoriyni klonlash
```bash
git clone https://github.com/Muxammadaziz-boss/Qadrdon-Ai.git
cd Qadrdon-Ai
```

### 2. Virtual muhit yaratish
```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Muhit o'zgaruvchilarini sozlash
`.env.example` faylidan `.env` nusxasini yarating:
```bash
cp .env.example .env
```
Faylni tahrirlab, o'z kalitlaringizni kiriting:
```ini
# BotFather'dan olingan asosiy bot tokeni
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Administrator Telegram ID raqamlari
ADMIN_IDS=12345678,87654321
ADMIN_USERNAME=@admin_username
CARD_NUMBER=8600000000000000
CARD_HOLDER=Qadirdon AI

# Google Gemini API kaliti
GEMINI_API_KEY=AIzaSy...

# Ma'lumotlar bazasi (standart SQLite yoki PostgreSQL)
DATABASE_URL=sqlite+aiosqlite:///./qadirdon_ai.db
```

### 5. Botda Business Rejimni Faollashtirish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/mybots` buyrug'i orqali o'z botingizni tanlang.
3. **Bot Settings** ➡️ **Business Mode** menyusiga kiring va uni **Turn On** (Yoqish) qiling.

### 6. Botni Shaxsiy Telegram Profilingizga Bog'lash
1. Telegram mobil ilovasida: **Sozlamalar** (Settings) ➡️ **Telegram Business**.
2. **Chat-botlar** (Chatbots) bo'limini tanlang.
3. Botingizning username'ini kiriting va unga xabarlarni boshqarish huquqini bering.
4. Bot darhol sizga Telegram Business ulanishi haqida tasdiqlovchi xabar yuboradi.

### 7. Loyihani ishga tushirish
```bash
python run.py
```

---

## 🧪 Testlarni Ishga Tushirish

Loyihadagi barcha asosiy modullar (AI dvigateli, personajlar, sozlash bosqichlari, munosabat tizimi) to'liq avtomatlashtirilgan testlar bilan qoplangan:

```bash
python -m pytest -v
```

---

## 🐳 Docker orqali ishga tushirish

Loyiha to'liq konteynerlashtirilgan bo'lib, PostgreSQL va Redis bilan birga ishga tushadi:

```bash
docker-compose up -d --build
```

---

## 📄 Litsenziya

Ushbu loyiha [MIT License](LICENSE) asosida litsenziyalangan.

---

<div align="center">
Yaratuvchi: <b>Muxammadaziz</b> &bull; Qadirdon AI Jamoasi (2026)
</div>
