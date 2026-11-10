"""Rollar va ovoz profillari testi."""

from ai.prompts.personality import get_full_system_prompt
from ai.prompts.roles import ROLES, ROLE_NAMES_UZ
from voice.voice_profiles import VOICE_PROFILES
from bot.handlers.setup_voice import VOICE_TYPES


def test_all_roles_render():
    for role_key in ROLES:
        prompt = get_full_system_prompt(role=role_key, ai_name="TestAI")
        assert "TestAI" in prompt
        assert role_key in ROLE_NAMES_UZ


def test_all_voice_types_in_profiles():
    # Setup_voice dagi har bir ovoz VOICE_PROFILES da mavjud bo'lishi shart
    for voice_key in VOICE_TYPES:
        assert voice_key in VOICE_PROFILES

