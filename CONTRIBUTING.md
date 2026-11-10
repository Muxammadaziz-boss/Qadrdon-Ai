# 🤝 Qadirdon AI — Loyihaga Hissa Qo'shish (Contributing Guide)

Qadirdon AI loyihasiga qiziqish bildirganingiz uchun tashakkur! Loyihani rivojlantirish, yangi personajlar qo'shish yoki xatoliklarni to'g'rilash bo'yicha qo'llanma bilan tanishing.

---

## 🛠️ Dasturiy Muhitni O'rnatish

1. Repozitoriyni klon qiling:
   ```bash
   git clone https://github.com/Muxammadaziz-boss/Qadrdon-Ai.git
   cd Qadrdon-Ai
   ```

2. Virtual muhit yarating va faollashtiring:
   ```bash
   python -m venv venv
   # Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # Linux/macOS:
   source venv/bin/activate
   ```

3. Bog'liqliklarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```

4. Muhit o'zgaruvchilarini sozlang:
   ```bash
   cp .env.example .env
   ```

---

## 🧪 Testlarni Ishga Tushirish

Barcha funksiyalar va testlar `pytest` orqali tekshiriladi:
```bash
python -m pytest
```

Alohida modul testlari:
```bash
# Setup wizard testi
python -m pytest tests/test_setup_wizard.py

# Personaj modellarini tekshirish
python -m pytest tests/test_character_models.py

# Humanizer dvigateli testi
python -m pytest tests/test_humanizer.py
```

---

## 🎭 Yangi Personaj Modeli Qo'shish

Yangi personaj modelini qo'shish uchun `ai/characters/` papkasidagi tegishli rol faylini oching (masalan, `qiz_dost_models.py` yoki `ayol_models.py`):

```python
{
    "id": "model_id",          # Unikal identifikator (kichik harflar va pastki chiziq)
    "name": "Ismi",            # Personaj ismi
    "age": 22,                 # Yoshi
    "location": "Manzili",      # Yashash shahri/viloyati
    "profession": "Kasbi",     # Kasbi yoki mashg'uloti
    "badge": "🌸",             # Emojisi
    "bio": "Personajning qisqacha tarixi va xarakteri...",
    "schedule": "Kun tartibi...",
    "speech_style": {
        "slangs": ["gap yo'q", "zo'r", "jonim"],
        "quirks": "Gapirish uslubidagi o'ziga xosliklar",
    },
    "secrets": {
        "level_3": "3-darajada ochiladigan sir...",
        "level_4": "4-darajada ochiladigan sir...",
        "level_5": "5-darajada ochiladigan eng chuqur sir...",
    },
}
```

Model qo'shilgach:
1. `tests/test_character_models.py` testini ishga tushiring.
2. `CHARACTERS.md` fayliga yangi model haqidagi ma'lumotni kiriting.

---

## 📌 Kodlash Standartlari

- **Python versiyasi**: Python 3.11+
- **Tipizatsiya**: Barcha funksiyalar va metodlarda to'liq type hint'lardan foydalaning (`from __future__ import annotations`).
- **Asinxronlik**: Barcha handlerlar va DB chaqiruvlari `async`/`await` asosida bo'lishi shart.
- **Madaniy moslik**: Personaj dialoglari va promptlari o'zbek xalqining milliy madaniyati va samimiy muloqot odobiga to'liq mos kelishi lozim.

---

## 🚀 Pull Request Yuborish

1. O'z fork yoki yangi tarmog'ingizni oching (`git checkout -b feature/ajoyib-xususiyat`).
2. O'zgarishlarni kiriting va testlarni tekshiring (`pytest`).
3. Commit qiling (`git commit -m "feat: yangi xususiyat qo'shildi"`).
4. O'z tarmog'ingizga push qiling va GitHub'da **Pull Request** oching.
