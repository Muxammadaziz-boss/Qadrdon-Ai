"""Qadirdon AI — Personality promptrini to'liq yig'uvchi modul."""

from ai.prompts.base import build_system_prompt
from ai.prompts.roles import ROLES
from ai.prompts.relationship_levels import get_role_level_prompt
from ai.characters import get_character_model


def get_full_system_prompt(
    role: str,
    ai_name: str,
    personality_prompt: str = "",
    language: str = "uz",
    emoji_level: int = 2,
    custom_phrases: dict | None = None,
    relationship_level: int = 1,
    game_mode: str = "story",
    character_id: str | None = None,
) -> str:
    """Rol moduli va qo'shimcha parametrlardan to'liq prompt yaratadi."""
    role_module = ROLES.get(role, ROLES["aka"])
    role_template = getattr(role_module, "ROLE_PROMPT", "")
    formatted_role_prompt = role_template.format(ai_name=ai_name)

    level_addon = get_role_level_prompt(role, relationship_level, game_mode)

    char_addon = ""
    if character_id:
        char_model = get_character_model(role, character_id)
        if char_model:
            char_addon = (
                f"\nANIQ PERSONAJ DOSSIYESI:\n"
                f"- Ismi: {char_model['name']}, Yoshi: {char_model['age']}\n"
                f"- Kasbi: {char_model['profession']}\n"
                f"- Yashash joyi: {char_model['location']}\n"
                f"- Hayoti va o'tmishi: {char_model['bio']}\n"
                f"- Kun tartibi: {char_model['schedule']}\n"
                f"- O'ziga xos iboralari: {', '.join(char_model.get('slangs', []))}\n"
            )

    full_role_prompt = f"{formatted_role_prompt}\n{level_addon}\n{char_addon}"

    return build_system_prompt(
        role=role,
        ai_name=ai_name,
        role_prompt=full_role_prompt,
        personality_prompt=personality_prompt,
        language=language,
        emoji_level=emoji_level,
        custom_phrases=custom_phrases,
    )


# Alias for backward compatibility
build_personality_prompt = get_full_system_prompt

