"""Qadirdon AI — Master Style Adapter.

Barcha humanizer modullarini birlashtirib insondek jonli matn tayyorlaydi.
"""

from ai.humanizer.emoji_inserter import insert_emojis
from ai.humanizer.slang_mixer import mix_slang
from ai.humanizer.typo_maker import add_typos
from ai.prompts.roles import ROLES


def humanize(text: str, ai_profile) -> tuple[str, str | None]:
    """
    AI javobini insoniy shaklga keltiradi.
    Returns:
        (humanized_text, correction_text_or_none)
    """
    role_module = ROLES.get(getattr(ai_profile, "role", "aka"), ROLES["aka"])
    role_emojis = getattr(role_module, "EMOJI_SET", ["😊", "👍"])

    # 1. Slang qo'llash
    if getattr(ai_profile, "use_slang", True):
        text = mix_slang(text, use_slang=True)

    # 2. Emojilar qo'shish
    emoji_level = getattr(ai_profile, "emoji_level", 2)
    text = insert_emojis(text, emoji_level=emoji_level, role_emojis=role_emojis)

    # 3. Kichik xatolar (typo)
    correction = None
    if getattr(ai_profile, "use_typos", True):
        text, correction = add_typos(text, probability=0.06)

    return text, correction
