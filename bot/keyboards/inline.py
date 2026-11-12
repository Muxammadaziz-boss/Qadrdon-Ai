"""Qadirdon AI — Inline klaviaturalar."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# ── Til tanlash (Language selection) ─────────────────────────────────────────
def language_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash klaviaturasi / Language selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇺🇿 O'zbekcha", callback_data="lang:uz"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский", callback_data="lang:ru"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🇬🇧 English", callback_data="lang:en"
                ),
            ],
        ]
    )


# ── Rol tanlash (Role selection) ─────────────────────────────────────────────
ROLES = [
    ("👨 Aka", "role:aka"),             # Older brother
    ("👦 Uka", "role:uka"),             # Younger brother
    ("👩 Opa", "role:opa"),             # Older sister
    ("👧 Singil", "role:singil"),       # Younger sister
    ("🤱 Ona", "role:ona"),             # Mother
    ("💕 Qiz do'st", "role:qiz_dost"),  # Girlfriend
    ("💍 Ayol", "role:ayol"),          # Wife
]


def role_keyboard() -> InlineKeyboardMarkup:
    """Rol tanlash klaviaturasi / Role selection keyboard."""
    buttons = []
    for text, cb_data in ROLES:
        buttons.append([InlineKeyboardButton(text=text, callback_data=cb_data)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def character_model_keyboard(role: str) -> InlineKeyboardMarkup:
    """Personaj modellari tanlash klaviaturasi."""
    from ai.characters import list_character_models
    models = list_character_models(role)
    buttons = []
    for model_id, info in models.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{info['badge']} {info['name']} ({info['age']} yosh)",
                callback_data=f"charmodel:{model_id}",
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text="🔙 Boshqa rolni tanlash",
            callback_data="back_to_roles",
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── O'yin rejimi (Game mode) ────────────────────────────────────────────────
def game_mode_keyboard() -> InlineKeyboardMarkup:
    """Sozlash jarayonida o'yin rejimini tanlash klaviaturasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Zabt etish (Story) — Noldan boshlash",
                    callback_data="setup_mode:story",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌟 Klassik — To'liq yaqinlik (5-daraja)",
                    callback_data="setup_mode:classic",
                )
            ],
        ]
    )


# ── Emoji darajasi (Emoji level) ─────────────────────────────────────────────
def emoji_level_keyboard() -> InlineKeyboardMarkup:
    """Emoji darajasi tanlash / Emoji level selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="😐 Kam", callback_data="emoji:1"),
                InlineKeyboardButton(text="🙂 O'rta", callback_data="emoji:2"),
                InlineKeyboardButton(text="😍 Ko'p", callback_data="emoji:3"),
            ],
        ]
    )


# ── Yozish tezligi (Typing speed) ───────────────────────────────────────────
def typing_speed_keyboard() -> InlineKeyboardMarkup:
    """Yozish tezligi tanlash / Typing speed selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🐢 Sekin", callback_data="speed:1"),
                InlineKeyboardButton(text="🚶 Normal", callback_data="speed:2"),
                InlineKeyboardButton(text="⚡ Tez", callback_data="speed:3"),
            ],
        ]
    )


# ── Tasdiqlash (Confirmation) ────────────────────────────────────────────────
def confirm_keyboard() -> InlineKeyboardMarkup:
    """Tasdiqlash / Bekor qilish klaviaturasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash", callback_data="confirm:yes"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish", callback_data="confirm:no"
                ),
            ],
        ]
    )


# ── Sozlamalar menyusi (Settings menu) ───────────────────────────────────────
def settings_keyboard() -> InlineKeyboardMarkup:
    """Asosiy sozlamalar menyusi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎭 Rolni o'zgartirish", callback_data="settings:role"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Ismni o'zgartirish", callback_data="settings:name"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💬 Xarakterni o'zgartirish", callback_data="settings:personality"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="😊 Emoji darajasi", callback_data="settings:emoji"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⌨️ Yozish tezligi", callback_data="settings:speed"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌐 Tilni o'zgartirish", callback_data="settings:language"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📖 Munosabatlar Kundaligi", callback_data="diary:show"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❤️ Munosabat darajasi va Rejim", callback_data="settings:relationship"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📋 Personaj anketasi (Dossye)", callback_data="settings:dossier"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎯 Kvestlar va Sirlar", callback_data="settings:quests"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔊 Ovoz va Emotsiya sozlamalari", callback_data="settings:voice"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 AI ni yoqish/o'chirish", callback_data="settings:toggle_ai"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga", callback_data="settings:back"
                ),
            ],
        ]
    )


# ── Balans va Tariflar klaviaturasi ──────────────────────────────────────────
def balance_keyboard() -> InlineKeyboardMarkup:
    """Foydalanuvchi balansi va tarif xarid qilish menyusi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Hisobni to'ldirish (Yo'riqnoma)",
                    callback_data="pay:instructions",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🥉 Standard (35,000 so'm / oy)",
                    callback_data="buy_plan:standard",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🥈 Premium (75,000 so'm / oy)",
                    callback_data="buy_plan:premium",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🥇 Ultra VIP (150,000 so'm / oy)",
                    callback_data="buy_plan:ultra",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Yangilash", callback_data="pay:refresh"
                ),
            ],
        ]
    )


# ── Orqaga (Back) ───────────────────────────────────────────────────────────
def back_keyboard() -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back"),
            ],
        ]
    )


# ── Sozlamalar ichidagi yordamchi klaviaturalar ──────────────────────────────
def settings_role_keyboard() -> InlineKeyboardMarkup:
    """Sozlamalar ichida rolni o'zgartirish klaviaturasi."""
    buttons = []
    for text, cb_data in ROLES:
        role_key = cb_data.split(":")[1]
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"set_role:{role_key}")])
    buttons.append([InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="settings:show")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def settings_language_keyboard() -> InlineKeyboardMarkup:
    """Sozlamalar ichida tilni o'zgartirish klaviaturasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang:uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")],
            [InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="settings:show")],
        ]
    )


def settings_voice_keyboard(role: str = "qiz_dost", show_all: bool = False) -> InlineKeyboardMarkup:
    """Sozlamalar ichida ovozni o'zgartirish klaviaturasi."""
    FEMALE_ROLES = {"qiz_dost", "ayol", "ona", "opa", "singil"}
    MALE_ROLES = {"aka", "uka"}

    all_voices = {
        "female_soft": "👩 Ayol — Yumshoq va mayin",
        "female_bright": "👩‍🦰 Ayol — Yorqin va sho'x",
        "female_calm": "🧕 Ayol — Vazmin va samimiy",
        "female_warm": "🌸 Ayol — Mehribon va iliq",
        "male_warm": "👨 Erkak — Samimiy va iliq",
        "male_deep": "🧔‍♂️ Erkak — Salobatli va past",
        "male_calm": "👨‍💼 Erkak — Vazmin va bosiq",
        "male_energetic": "⚡ Erkak — Qat'iyatli yigit",
        "child_playful": "🧒 Bola / Kenjatoy — Quvnoq",
    }

    buttons = [
        [
            InlineKeyboardButton(
                text="🎭 Emotsiya va Ohangni tanlash",
                callback_data="settings:emotions",
            )
        ]
    ]
    if show_all:
        for key, label in all_voices.items():
            buttons.append([
                InlineKeyboardButton(text=label, callback_data=f"set_voice:{key}"),
                InlineKeyboardButton(text="▶️ Tinglash", callback_data=f"preview_voice:{key}"),
            ])
        buttons.append([InlineKeyboardButton(text="🔙 Mos ovozlarga qaytish", callback_data=f"set_vmode:filter:{role}")])
    else:
        if role in FEMALE_ROLES:
            keys = ["female_soft", "female_bright", "female_calm", "female_warm"]
            if role == "singil":
                keys.append("child_playful")
        elif role in MALE_ROLES:
            keys = ["male_warm", "male_deep", "male_calm", "male_energetic"]
            if role == "uka":
                keys.append("child_playful")
        else:
            keys = list(all_voices.keys())

        for key in keys:
            label = all_voices.get(key, key)
            buttons.append([
                InlineKeyboardButton(text=label, callback_data=f"set_voice:{key}"),
                InlineKeyboardButton(text="▶️ Tinglash", callback_data=f"preview_voice:{key}"),
            ])
        buttons.append([InlineKeyboardButton(text="🌐 Barcha ovozlar", callback_data=f"set_vmode:all:{role}")])

    buttons.append([InlineKeyboardButton(text="⏩ Ovozni o'chirish", callback_data="set_voice:off")])
    buttons.append([InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="settings:show")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def settings_emotion_keyboard(current_emotion: str = "auto") -> InlineKeyboardMarkup:
    """Emotsiya va intonatsiya ohangini tanlash hamda eshitib ko'rish klaviaturasi."""
    emotions = [
        ("romantic", "❤️ Romantik / Mehrli"),
        ("joyful", "😂 Quvnoq / Xushchaqchaq"),
        ("playful", "😜 Sho'x / Nozli (Erka)"),
        ("comforting", "🫂 Tasalli / Dalda"),
        ("surprised", "😲 Hayrat / Hayajon"),
        ("serious", "🤔 Jiddiy / O'ychan"),
        ("calm", "🌸 Sokin / Vazmin"),
    ]

    auto_check = "✅ " if current_emotion in {"auto", "", None} else ""
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{auto_check}🎭 Avtomatik (Mazmunga qarab)",
                callback_data="set_emotion:auto",
            )
        ]
    ]

    for key, label in emotions:
        check = "✅ " if current_emotion == key else ""
        buttons.append([
            InlineKeyboardButton(text=f"{check}{label}", callback_data=f"set_emotion:{key}"),
            InlineKeyboardButton(text="▶️ Tinglash", callback_data=f"preview_emotion:{key}"),
        ])

    buttons.append([
        InlineKeyboardButton(text="🔙 Ovoz sozlamalariga qaytish", callback_data="settings:voice"),
    ])
    buttons.append([
        InlineKeyboardButton(text="⚙️ Asosiy sozlamalar", callback_data="settings:show"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def settings_models_keyboard(role: str) -> InlineKeyboardMarkup:
    """Sozlamalar ichida modelni almashtirish klaviaturasi."""
    from ai.characters import list_character_models
    models = list_character_models(role)
    buttons = []
    for model_id, info in models.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{info['badge']} {info['name']}",
                callback_data=f"set_model:{model_id}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Sozlamalarga qaytish", callback_data="settings:show")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def relationship_settings_keyboard(current_mode: str = "story") -> InlineKeyboardMarkup:
    """Muloqot darajalari va o'yin rejimini boshqarish klaviaturasi."""
    story_check = "✅ " if current_mode == "story" else ""
    classic_check = "✅ " if current_mode == "classic" else ""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{story_check}🎮 Zabt etish rejimi (Noldan boshlash)",
                    callback_data="rel:mode:story",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{classic_check}🌟 Klassik rejim (Maksimal yaqinlik)",
                    callback_data="rel:mode:classic",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Darajani 1-bosqichga nollash",
                    callback_data="rel:reset",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="settings:show",
                )
            ],
        ]
    )
