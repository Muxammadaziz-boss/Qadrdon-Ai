"""Humanizer testlari."""

from ai.humanizer.slang_mixer import mix_slang
from ai.humanizer.typo_maker import add_typos
from ai.humanizer.emoji_inserter import insert_emojis


def test_slang_mixer_quotes_and_punctuation():
    # Matn ichidagi qo'shtirnoq va tinish belgilari buzilmasligini tekshirish
    text = '"Rahmat!" deb aytdi.'
    res = mix_slang(text, use_slang=True)
    assert res.endswith("deb aytdi.")
    # Qo'shtirnoq va undov belgisi saqlangan bo'lishi kerak
    assert res.startswith('"')
    assert "!" in res.split("deb")[0]


def test_slang_mixer_disabled():
    text = "Salom rahmat mayli"
    assert mix_slang(text, use_slang=False) == text


def test_add_typos_probability_zero():
    text = "Salom do'stim qandaysan"
    corrupted, correction = add_typos(text, probability=0.0)
    assert corrupted == text
    assert correction is None


def test_insert_emojis():
    text = "Assalomu alaykum"
    res = insert_emojis(text, emoji_level=0, role_emojis=["👍"])
    assert res == text

