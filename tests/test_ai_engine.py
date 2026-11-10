"""AI Engine xabarlar ketma-ketligi va duplikatsiya testlari."""

from ai.engine import AiEngine


def test_prepare_gemini_contents_deduplication():
    engine = AiEngine()
    history = [
        {"role": "user", "content": "Salom"},
        {"role": "assistant", "content": "Salom! Ishlaringiz yaxshimi?"},
        {"role": "user", "content": "Rahmat yaxshi"},
    ]
    # Agar user_message allaqachon tarix oxirida bo'lsa
    contents = engine._prepare_gemini_contents(history, user_message="Rahmat yaxshi")

    # Jami 3 ta alohida Content bo'lishi kerak (user, model, user), 4 ta emas!
    assert len(contents) == 3
    assert contents[0].role == "user"
    assert contents[1].role == "model"
    assert contents[2].role == "user"
    assert contents[2].parts[0].text == "Rahmat yaxshi"


def test_prepare_gemini_contents_consecutive_user_merge():
    engine = AiEngine()
    history = [
        {"role": "user", "content": "Salom"},
        {"role": "user", "content": "Bugun nima gaplar?"},
    ]
    # Ketma-ket kelgan 2 ta user roli bitta turnga birlashishi kerak
    contents = engine._prepare_gemini_contents(history, user_message="")
    assert len(contents) == 1
    assert contents[0].role == "user"
    assert "Salom\nBugun nima gaplar?" in contents[0].parts[0].text

