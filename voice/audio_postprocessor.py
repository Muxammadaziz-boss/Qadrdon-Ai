"""Qadirdon AI — Audio Post-Processor (Smartfon Mikrofoni va Telegram Voice Filter).

TTS orqali olingan toza laboratoriya audiosini Telegram smartfon ovozli xabariga
moslab qayta ishlaydi:
1. Telefon mikrofoni ekvalayzeri (yaqinlik effekti, mayinlik).
2. Yuqori chastotali sun'iy shovqinni (sibilance) kesish.
3. Dinamik kompressor (ovozni barqarorlashtirish).
4. Telegram standartidagi native Opus (.ogg, 48kHz, mono) formatiga konvertatsiya qilish.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from loguru import logger


def get_ffmpeg_exe() -> str | None:
    """Tizimdagi yoki imageio_ffmpeg paketidagi ffmpeg dasturini topadi."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except Exception:
        pass

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    return None


async def apply_smartphone_voice_filter(
    input_path: str,
    output_format: str = "ogg",
) -> str:
    """
    Ovoz fayliga haqiqiy smartfon mikrofoni filtrlarini beradi va
    Telegram uchun rasmiy Opus (.ogg) formatiga o'tkazadi.
    
    Agar ffmpeg bo'lmasa yoki xatolik yuz bersa, asl fayl xavfsiz qaytariladi.
    """
    if not input_path or not os.path.exists(input_path):
        return input_path

    ffmpeg_exe = get_ffmpeg_exe()
    if not ffmpeg_exe:
        logger.debug("FFmpeg topilmadi, asl audio fayl ishlatiladi.")
        return input_path

    # Telegram uchun rasmiy ovozli xabar kengaytmasi
    suffix = f".{output_format}"
    fd, out_path = tempfile.mkstemp(suffix=suffix, prefix="qadirdon_voice_note_")
    os.close(fd)

    # Smartfon mikrofoni va xona filtr zanjiri:
    # 1. highpass=f=80: 80Hz dan past sun'iy to'lqinlarni qirqish
    # 2. lowpass=f=7800: 7.8kHz dan yuqori metallik/robotik shovqinni yo'qotish
    # 3. equalizer=f=2800:width_type=o:width=1.5:g=2.2: ovozga iliq yaqinlik berish
    # 4. acompressor: tovush balandligini bir maromda ushlab turish
    audio_filter = (
        "highpass=f=80,"
        "lowpass=f=7800,"
        "equalizer=f=2800:width_type=o:width=1.5:g=2.2,"
        "acompressor=threshold=-18dB:ratio=2.2:attack=10:release=100:makeup=2dB"
    )

    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", input_path,
        "-af", audio_filter,
        "-c:a", "libopus",
        "-b:a", "32k",
        "-ar", "48000",
        "-ac", "1",
        out_path,
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, stderr = await proc.communicate()

        if proc.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 100:
            # Asl vaqtinchalik xom faylni o'chirib, o'rniga qayta ishlangan OGG ni qaytaramiz
            Path(input_path).unlink(missing_ok=True)
            logger.info(
                "Audio post-processing muvaffaqiyatli: {} ({} bayt)",
                out_path,
                os.path.getsize(out_path),
            )
            return out_path
        else:
            logger.warning(
                "FFmpeg qayta ishlashda xatolik (rc={}): {}",
                proc.returncode,
                stderr.decode("utf-8", errors="ignore")[:150],
            )
            Path(out_path).unlink(missing_ok=True)
            return input_path

    except Exception as exc:
        logger.warning("Audio post-processing ijrosida xato: {}, asl fayl qaytarilmoqda", exc)
        Path(out_path).unlink(missing_ok=True)
        return input_path
