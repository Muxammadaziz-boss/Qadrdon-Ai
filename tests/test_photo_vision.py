"""Unit tests for Multimodal AI Photo Vision Analysis."""

import asyncio
import pytest
from google.genai import types

from ai.engine import AiEngine
from db.models import AiProfile


def test_prepare_gemini_contents_with_image():
    """Rasm baytlari bilan Gemini kontentlari to'g'ri shakllanishini tekshiradi."""
    engine = AiEngine()
    fake_img = b"\xff\xd8\xff\xe0\x00\x10JFIF"  # Minimal JPEG header bytes

    contents = engine._prepare_gemini_contents(
        conversation_history=[],
        user_message="Bu mening mushukcham",
        image_bytes=fake_img,
        image_mime_type="image/jpeg",
    )

    assert len(contents) == 1
    last_turn = contents[-1]
    assert last_turn.role == "user"
    assert len(last_turn.parts) == 2  # image part + text part

    # Birinchi part rasm bo'lishi kerak
    img_part = last_turn.parts[0]
    assert img_part.inline_data is not None
    assert img_part.inline_data.mime_type == "image/jpeg"
    assert img_part.inline_data.data == fake_img

    # Ikkinchi part matn bo'lishi kerak
    text_part = last_turn.parts[1]
    assert text_part.text == "Bu mening mushukcham"


def test_prepare_gemini_contents_image_without_caption():
    """Caption berilmaganda ham standart yo'riqnoma qo'shilishini tekshiradi."""
    engine = AiEngine()
    fake_img = b"\xff\xd8\xff\xe0\x00\x10JFIF"

    contents = engine._prepare_gemini_contents(
        conversation_history=[],
        user_message="",
        image_bytes=fake_img,
    )

    assert len(contents) == 1
    last_turn = contents[-1]
    assert len(last_turn.parts) == 2
    assert "rasmda nima borligini" in last_turn.parts[1].text.lower()


def test_generate_response_multimodal():
    """Multimodal rasm tahlili orqali javob generatsiya qilishni tekshiradi."""
    engine = AiEngine()
    profile = AiProfile(
        role="qiz_dost",
        ai_name="Malika",
        relationship_level=1,
        game_mode="story",
    )
    fake_img = b"\xff\xd8\xff\xe0\x00\x10JFIF"

    res = asyncio.run(
        engine.generate_response(
            user_message="Mushugim qalay?",
            conversation_history=[],
            ai_profile=profile,
            image_bytes=fake_img,
        )
    )

    assert "text" in res
    assert isinstance(res["text"], str)
    assert len(res["text"]) > 0
