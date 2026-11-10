"""Unit tests for the Relationship Progression System (Muloqot darajalari)."""

import pytest
from ai.prompts.relationship_levels import (
    RELATIONSHIP_LEVELS,
    calculate_level_from_xp,
    get_level_info,
    get_role_level_prompt,
    get_progress_bar,
)
from ai.trust_evaluator import evaluate_message_trust
from ai.prompts.roles import ROLES


def test_all_seven_roles_have_five_levels():
    """Barcha 7 ta personaj 5 ta to'liq darajaga ega ekanligini tekshiradi."""
    expected_roles = ["aka", "uka", "opa", "singil", "ona", "qiz_dost", "ayol"]
    for role in expected_roles:
        assert role in RELATIONSHIP_LEVELS, f"{role} RELATIONSHIP_LEVELS ichida topilmadi"
        role_data = RELATIONSHIP_LEVELS[role]
        for lvl in range(1, 6):
            assert lvl in role_data, f"{role} uchun {lvl}-daraja topilmadi"
            lvl_info = role_data[lvl]
            assert "title" in lvl_info and lvl_info["title"]
            assert "badge" in lvl_info and lvl_info["badge"]
            assert "desc" in lvl_info and lvl_info["desc"]
            assert "prompt" in lvl_info and lvl_info["prompt"]


def test_calculate_level_from_xp():
    """XP ballari bo'yicha darajani aniqlash to'g'riligini tekshiradi."""
    assert calculate_level_from_xp(0) == 1
    assert calculate_level_from_xp(50) == 1
    assert calculate_level_from_xp(100) == 2
    assert calculate_level_from_xp(299) == 2
    assert calculate_level_from_xp(300) == 3
    assert calculate_level_from_xp(599) == 3
    assert calculate_level_from_xp(600) == 4
    assert calculate_level_from_xp(999) == 4
    assert calculate_level_from_xp(1000) == 5
    assert calculate_level_from_xp(1500) == 5


def test_get_role_level_prompt_modes():
    """Story va Classic rejimlarida prompt to'g'ri shakllanishini tekshiradi."""
    # Story mode: 1-daraja
    prompt_lvl1 = get_role_level_prompt("qiz_dost", level=1, game_mode="story")
    assert "1-daraja (Notanish qiz / Begona)" in prompt_lvl1
    assert "Siz" in prompt_lvl1

    # Story mode: 4-daraja
    prompt_lvl4 = get_role_level_prompt("qiz_dost", level=4, game_mode="story")
    assert "4-daraja (Qiz do'st / Sevgili)" in prompt_lvl4

    # Classic mode: avtomatik 5-daraja
    prompt_classic = get_role_level_prompt("qiz_dost", level=1, game_mode="classic")
    assert "5-daraja (Yurakdosh / Vafodor yor)" in prompt_classic
    assert "Klassik" in prompt_classic


def test_evaluate_message_trust_positive():
    """Ijobiy xabarlarda XP oshishini tekshiradi."""
    res = evaluate_message_trust(
        user_text="Assalomu alaykum, yaxshimisiz? Ovqatlandingizmi, charchamadingizmi?",
        current_xp=50,
        current_level=1,
        role="qiz_dost",
        game_mode="story",
    )
    assert res["delta_xp"] > 0
    assert res["new_xp"] > 50


def test_evaluate_message_trust_negative():
    """Salbiy/haqoratli xabarlarda XP tushishini tekshiradi."""
    res = evaluate_message_trust(
        user_text="Yo'qol, asabimga tegma jinni!",
        current_xp=150,
        current_level=2,
        role="qiz_dost",
        game_mode="story",
    )
    assert res["delta_xp"] < 0
    assert res["new_xp"] < 150


def test_evaluate_message_trust_level_up():
    """XP chegaradan oshganda leveled_up bayrog'i yoqilishini tekshiradi."""
    # 95 XP da +10 yoki undan ko'p olsa 100+ bo'lib 2-darajaga chiqishi kerak
    res = evaluate_message_trust(
        user_text="Assalomu alaykum! Rahmat sizga, yaxshiyam borsiz!",
        current_xp=95,
        current_level=1,
        role="qiz_dost",
        game_mode="story",
    )
    assert res["leveled_up"] is True
    assert res["new_level"] == 2


def test_progress_bar_format():
    """Progress bar to'g'ri foiz va formatda chiqishini tekshiradi."""
    bar = get_progress_bar(xp=50, level=1)
    assert "50%" in bar
    assert "50/100 XP" in bar

    max_bar = get_progress_bar(xp=1000, level=5)
    assert "MAKSIMAL" in max_bar
