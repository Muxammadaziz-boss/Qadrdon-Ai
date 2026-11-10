"""Setup wizard testlari."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey

from bot.handlers.setup_personality import on_emoji_level_chosen
from bot.handlers.setup_role import (
    on_role_chosen,
    on_character_model_chosen,
    on_game_mode_chosen,
)
from bot.handlers.setup_voice import on_typing_speed_chosen, voice_type_keyboard
from bot.states.setup import SetupStates
from db.models import User


@pytest.mark.anyio
async def test_on_role_chosen_shows_available_models():
    """Rol tanlanganda faqat mavjud personajlar chiqishi va custom variant bo'lmasligini tekshiradi."""
    storage = MemoryStorage()
    key = StorageKey(bot_id=123, chat_id=456, user_id=789)
    state = FSMContext(storage=storage, key=key)

    await state.set_state(SetupStates.choosing_role)

    call = MagicMock()
    call.data = "role:qiz_dost"
    call.answer = AsyncMock()
    call.message = MagicMock()
    call.message.edit_text = AsyncMock()

    user = User(id=1, telegram_id=789, full_name="Test")

    await on_role_chosen(call, state, user)

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.call_args
    text = args[0]
    kb = kwargs.get("reply_markup")

    assert "Mavjud hayotiy personajlardan birini tanlang" in text
    cbs = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "charmodel:rayhona" in cbs
    assert "charmodel:kamola" in cbs
    assert "charmodel:custom" not in cbs  # Custom variant yo'q, faqat mavjudlar


@pytest.mark.anyio
async def test_on_character_model_chosen_to_game_mode():
    """Mavjud personaj tanlanganda o'yin rejimi (Story vs Classic) tanlashga o'tishini tekshiradi."""
    storage = MemoryStorage()
    key = StorageKey(bot_id=123, chat_id=456, user_id=789)
    state = FSMContext(storage=storage, key=key)

    await state.set_state(SetupStates.choosing_character_model)
    await state.update_data(role="qiz_dost")

    call = MagicMock()
    call.data = "charmodel:rayhona"
    call.answer = AsyncMock()
    call.message = MagicMock()
    call.message.edit_text = AsyncMock()

    await on_character_model_chosen(call, state)

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.call_args
    text = args[0]
    kb = kwargs.get("reply_markup")

    assert "Rayhona" in text
    assert "1-qadam" in text
    assert "Zabt etish" in text
    cbs = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "setup_mode:story" in cbs
    assert "setup_mode:classic" in cbs

    current_state = await state.get_state()
    assert current_state == SetupStates.choosing_game_mode.state

    data = await state.get_data()
    assert data["ai_name"] == "Rayhona"
    assert data["character_id"] == "rayhona"


@pytest.mark.anyio
async def test_on_game_mode_chosen():
    """O'yin rejimi tanlanganda uni saqlashi va emoji bosqichiga o'tishini tekshiradi."""
    storage = MemoryStorage()
    key = StorageKey(bot_id=123, chat_id=456, user_id=789)
    state = FSMContext(storage=storage, key=key)

    await state.set_state(SetupStates.choosing_game_mode)
    await state.update_data(ai_name="Rayhona")

    call = MagicMock()
    call.data = "setup_mode:story"
    call.answer = AsyncMock()
    call.message = MagicMock()
    call.message.edit_text = AsyncMock()

    await on_game_mode_chosen(call, state)

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.call_args
    text = args[0]

    assert "2-qadam" in text
    assert "emoji" in text.lower()
    current_state = await state.get_state()
    assert current_state == SetupStates.setting_emoji_level.state

    data = await state.get_data()
    assert data["game_mode"] == "story"


@pytest.mark.anyio
async def test_on_emoji_level_chosen():
    storage = MemoryStorage()
    key = StorageKey(bot_id=123, chat_id=456, user_id=789)
    state = FSMContext(storage=storage, key=key)

    await state.set_state(SetupStates.setting_emoji_level)
    await state.update_data(ai_name="Begim")

    call = MagicMock()
    call.data = "emoji:2"
    call.answer = AsyncMock()
    call.message = MagicMock()
    call.message.edit_text = AsyncMock()

    user = User(id=1, telegram_id=789, full_name="Test")

    await on_emoji_level_chosen(call, state, user)

    # 1. Callback javob berilgan bo'lishi kerak
    call.answer.assert_awaited_once()

    # 2. Xabar tahrirlangan bo'lishi kerak
    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.call_args
    assert "Yozish tezligini tanlang" in args[0] or "yozsin" in args[0]
    assert kwargs.get("reply_markup") is not None

    # 3. Yangi holat setting_typing_speed bo'lishi kerak
    current_state = await state.get_state()
    assert current_state == SetupStates.setting_typing_speed.state

    # 4. FSM data'da emoji_level saqlangan bo'lishi kerak
    data = await state.get_data()
    assert data["emoji_level"] == 2


@pytest.mark.anyio
async def test_on_typing_speed_chosen_female_role():
    """Qiz do'st roli uchun ovoz tanlashda faqat mos ayol ovozlari chiqishini tekshiradi."""
    storage = MemoryStorage()
    key = StorageKey(bot_id=123, chat_id=456, user_id=789)
    state = FSMContext(storage=storage, key=key)

    await state.set_state(SetupStates.setting_typing_speed)
    await state.update_data(ai_name="malika", role="qiz_dost")

    call = MagicMock()
    call.data = "speed:3"
    call.answer = AsyncMock()
    call.message = MagicMock()
    call.message.edit_text = AsyncMock()

    user = User(id=1, telegram_id=789, full_name="Test")

    await on_typing_speed_chosen(call, state, user)

    call.message.edit_text.assert_awaited_once()
    args, kwargs = call.message.edit_text.call_args
    text = args[0]
    kb = kwargs.get("reply_markup")

    # Ism bosh harf bilan chiqishi kerak
    assert "Malika uchun mos ovozni tanlang" in text

    # Klaviaturada erkak ovozlari bo'lmasligi kerak (faqat ayol ovozlari)
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "voice:female_soft" in callbacks
    assert "voice:male_deep" not in callbacks
    assert "voice:skip" in callbacks


def test_voice_type_keyboard_role_filtering():
    """Rolga mos ovozlar filtrlanishini tekshiradi."""
    # Qiz do'st: ayol ovozlari
    qiz_kb = voice_type_keyboard(role="qiz_dost", show_all=False)
    qiz_cbs = [btn.callback_data for row in qiz_kb.inline_keyboard for btn in row]
    assert "voice:female_soft" in qiz_cbs
    assert "voice:male_warm" not in qiz_cbs
    assert "vmode:all:qiz_dost" in qiz_cbs

    # Aka: erkak ovozlari
    aka_kb = voice_type_keyboard(role="aka", show_all=False)
    aka_cbs = [btn.callback_data for row in aka_kb.inline_keyboard for btn in row]
    assert "voice:male_warm" in aka_cbs
    assert "voice:female_soft" not in aka_cbs
    assert "vmode:all:aka" in aka_cbs

    # Show all bo'lsa barcha ovozlar
    all_kb = voice_type_keyboard(role="qiz_dost", show_all=True)
    all_cbs = [btn.callback_data for row in all_kb.inline_keyboard for btn in row]
    assert "voice:female_soft" in all_cbs
    assert "voice:male_warm" in all_cbs
