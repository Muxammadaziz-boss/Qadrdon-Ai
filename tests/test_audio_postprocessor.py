"""Unit Tests for Audio Post-Processor (Smartphone Filter & Opus Conversion)."""

import os
import pytest
from voice.audio_postprocessor import get_ffmpeg_exe, apply_smartphone_voice_filter


def test_get_ffmpeg_exe():
    exe = get_ffmpeg_exe()
    assert exe is not None
    assert os.path.exists(exe)


@pytest.mark.anyio
async def test_apply_smartphone_voice_filter_nonexistent():
    # If file doesn't exist, returns input safely
    res = await apply_smartphone_voice_filter("non_existent_file.mp3")
    assert res == "non_existent_file.mp3"


@pytest.mark.anyio
async def test_apply_smartphone_voice_filter_real():
    import edge_tts
    import tempfile

    # Create dummy mp3 with edge-tts
    c = edge_tts.Communicate("Salom sinov", "uz-UZ-MadinaNeural")
    fd, temp_mp3 = tempfile.mkstemp(suffix=".mp3", prefix="test_raw_")
    os.close(fd)
    await c.save(temp_mp3)

    try:
        filtered_path = await apply_smartphone_voice_filter(temp_mp3, output_format="ogg")
        assert os.path.exists(filtered_path)
        assert filtered_path.endswith(".ogg")
        assert os.path.getsize(filtered_path) > 100
    finally:
        if os.path.exists(filtered_path):
            os.remove(filtered_path)
