"""Unit tests for the Character Models and Quests System across all roles."""

import pytest
from ai.characters import get_character_model, list_character_models
from ai.characters.qiz_dost_models import QIZ_DOST_MODELS
from ai.quests.manager import check_secret_quest_trigger, check_active_quest_completion
from ai.prompts.personality import get_full_system_prompt

ALL_ROLES = ["qiz_dost", "ayol", "ona", "aka", "uka", "opa", "singil"]


@pytest.mark.parametrize("role", ALL_ROLES)
def test_all_roles_have_six_complete_models(role: str):
    """Barcha 7 ta rol uchun kamida 6 ta model to'liq ma'lumotlar bilan mavjudligini tekshiradi."""
    models = list_character_models(role)
    assert len(models) >= 6, f"{role} roli uchun kamida 6 ta model bo'lishi kerak, mavjud: {len(models)}"

    for m_id, model in models.items():
        assert "name" in model and model["name"]
        assert "age" in model and isinstance(model["age"], int)
        assert "profession" in model and model["profession"]
        assert "location" in model and model["location"]
        assert "bio" in model and len(model["bio"]) > 20
        assert "schedule" in model and model["schedule"]
        assert "slangs" in model and len(model["slangs"]) > 0
        assert "secret_trigger" in model
        assert "keywords" in model["secret_trigger"]
        assert "story" in model["secret_trigger"]
        assert "quests" in model
        assert "normal" in model["quests"]
        assert "urgent" in model["quests"]


def test_get_character_model():
    """get_character_model to'g'ri modelni qaytarishini tekshiradi."""
    rayhona = get_character_model("qiz_dost", "rayhona")
    assert rayhona is not None
    assert rayhona["name"] == "Rayhona"
    assert rayhona["age"] == 21

    zarina = get_character_model("ayol", "zarina")
    assert zarina is not None
    assert zarina["name"] == "Zarina"

    fotima = get_character_model("ona", "fotima")
    assert fotima is not None
    assert "Fotima" in fotima["name"]

    none_model = get_character_model("qiz_dost", "non_existing_model")
    assert none_model is None


def test_secret_quest_trigger():
    """Yashirin kvest kalit so'z aytilganda ochilishini tekshiradi."""
    rayhona = get_character_model("qiz_dost", "rayhona")
    user_text = "Nega doim shu ko'k finjoningdan kofe ichasan?"

    # 1-marta: sir ochiladi
    secret = check_secret_quest_trigger(user_text, rayhona, unlocked_secrets=[])
    assert secret is not None
    assert secret["id"] == "rayhona_secret"
    assert secret["reward_xp"] == 80
    assert "Ko'k qahva finjoni" in secret["title"]

    # 2-marta: allaqachon ochilgan bo'lsa qayta ochilmaydi
    secret_again = check_secret_quest_trigger(user_text, rayhona, unlocked_secrets=["rayhona_secret"])
    assert secret_again is None


def test_active_quest_completion():
    """Oddiy va favqulodda kvestlar matn orqali bajarilishini tekshiradi."""
    rayhona = get_character_model("qiz_dost", "rayhona")
    urgent_q = rayhona["quests"]["urgent"]

    # Kvartira egasi janjal qilganda dalda berish
    res = check_active_quest_completion("Siqilma, men doim yoningdaman, birga hal qilamiz!", urgent_q)
    assert res is not None
    assert res["id"] == "rayhona_landlord"
    assert res["reward_xp"] == 50


def test_get_full_system_prompt_with_character():
    """Promptga personaj dossiyesi to'g'ri birikishini tekshiradi."""
    prompt = get_full_system_prompt(
        role="ayol",
        ai_name="Zarina",
        relationship_level=1,
        game_mode="story",
        character_id="zarina",
    )
    assert "ANIQ PERSONAJ DOSSIYESI" in prompt
    assert "Zarina" in prompt
    assert "Sergeli" in prompt
