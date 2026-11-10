"""Qadirdon AI — Qo'ng'iroq boshqaruvchisi.

Pyrogram + pytgcalls yordamida Telegram ovozli qo'ng'iroqlarni
boshqaradi: kiruvchi qo'ng'iroqlarni qabul qilish, tugatish va
AI dvigatel bilan bog'lash.

⚠️  EKSPERIMENTAL / KELAJAK XUSUSIYAT
    Telegram VoIP qo'ng'iroqlari hozircha cheklangan API orqali
    ishlaydi. pytgcalls kutubxonasi rasmiy emas va kelajakda
    o'zgarishi mumkin. Bu modul hozircha prototip sifatida
    ishlab chiqilgan.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine, Dict, Optional

from loguru import logger
from pyrogram import Client as PyrogramClient
from pytgcalls import PyTgCalls
from pytgcalls.types import Update as TgCallUpdate

from config.settings import settings
from voice.call_handler import CallConversationHandler


# ---------------------------------------------------------------------------
# Qo'ng'iroq holatlari
# ---------------------------------------------------------------------------
class CallState:
    """Bitta qo'ng'iroqning holati."""

    __slots__ = ("chat_id", "status", "handler", "_task")

    def __init__(self, chat_id: int) -> None:
        self.chat_id = chat_id
        self.status: str = "ringing"  # ringing | active | ended
        self.handler: Optional[CallConversationHandler] = None
        self._task: Optional[asyncio.Task] = None


class CallManager:
    """Telegram ovozli qo'ng'iroqlar menejeri.

    ⚠️  Eksperimental — pytgcalls API o'zgarishi mumkin.
    """

    def __init__(self) -> None:
        self._pyro_client: Optional[PyrogramClient] = None
        self._tgcalls: Optional[PyTgCalls] = None
        self._active_calls: Dict[int, CallState] = {}
        self._ai_handler: Optional[
            Callable[[str, str], Coroutine[Any, Any, str]]
        ] = None

    # ----- AI callback -----

    def set_ai_handler(
        self,
        handler: Callable[[str, str], Coroutine[Any, Any, str]],
    ) -> None:
        """AI javob beruvchi funksiyani o'rnatadi.

        handler(user_text: str, context: str) -> ai_response: str
        """
        self._ai_handler = handler

    # ----- Boshlash / To'xtatish -----

    async def start(self) -> None:
        """Pyrogram va pytgcalls mijozlarini ishga tushiradi.

        ⚠️  Buning uchun TELEGRAM_API_ID, TELEGRAM_API_HASH va
            TELEGRAM_PHONE muhit o'zgaruvchilari to'ldirilgan bo'lishi kerak.
            Birinchi ishga tushirishda Pyrogram sessiya kodi so'rashi mumkin.
        """
        if not settings.TELEGRAM_API_ID or not settings.TELEGRAM_API_HASH:
            logger.warning(
                "VoIP sozlamalari to'ldirilmagan — qo'ng'iroq moduli o'chirilgan"
            )
            return

        logger.info("Pyrogram mijoz ishga tushirilmoqda …")

        self._pyro_client = PyrogramClient(
            name="qadirdon_voip",
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH,
            phone_number=settings.TELEGRAM_PHONE,
        )

        await self._pyro_client.start()

        self._tgcalls = PyTgCalls(self._pyro_client)

        # Kiruvchi qo'ng'iroq hodisasi
        # ⚠️  pytgcalls API versiyasiga qarab hodisa nomi farq qilishi mumkin
        @self._tgcalls.on_update()
        async def _on_call_update(_, update: TgCallUpdate) -> None:
            await self._on_raw_update(update)

        await self._tgcalls.start()

        logger.info("VoIP qo'ng'iroq menejeri tayyor ✓")

    async def stop(self) -> None:
        """Barcha faol qo'ng'iroqlarni tugatadi va mijozlarni yopadi."""
        # Barcha faol qo'ng'iroqlarni tugatish
        chat_ids = list(self._active_calls.keys())
        for chat_id in chat_ids:
            await self.end_call(chat_id)

        if self._tgcalls:
            # pytgcalls yopish
            try:
                await self._tgcalls.stop()  # type: ignore[union-attr]
            except Exception as e:
                logger.warning("pytgcalls yopishda xato: {}", e)

        if self._pyro_client:
            await self._pyro_client.stop()

        logger.info("VoIP qo'ng'iroq menejeri to'xtatildi")

    # ----- Qo'ng'iroq boshqarish -----

    async def handle_incoming_call(self, call: Any) -> None:
        """Kiruvchi qo'ng'iroqni qabul qiladi va AI suhbatni boshlaydi.

        ⚠️  Bu metod pytgcalls ning kiruvchi qo'ng'iroq hodisasi orqali
            chaqiriladi. API barqaror emas.

        Args:
            call: pytgcalls ning qo'ng'iroq ob'ekti.
        """
        chat_id = getattr(call, "chat_id", None)
        if chat_id is None:
            logger.warning("Qo'ng'iroq ob'ektida chat_id topilmadi: {}", call)
            return

        if chat_id in self._active_calls:
            logger.warning("chat_id={} uchun qo'ng'iroq allaqachon faol", chat_id)
            return

        logger.info("Kiruvchi qo'ng'iroq: chat_id={}", chat_id)

        # Yangi qo'ng'iroq holati
        state = CallState(chat_id)
        self._active_calls[chat_id] = state

        try:
            # Qo'ng'iroqni qabul qilish
            # ⚠️  pytgcalls API versiyasiga bog'liq
            if self._tgcalls:
                # pytgcalls orqali qo'ng'iroqni qabul qilish
                # (API barqaror emas, kelajakda o'zgarishi mumkin)
                pass

            state.status = "active"

            # AI suhbat boshqaruvchisini yaratish
            state.handler = CallConversationHandler(
                chat_id=chat_id,
                ai_handler=self._ai_handler,
            )

            # Suhbat tsiklini fon vazifa sifatida ishga tushirish
            state._task = asyncio.create_task(
                state.handler.run_conversation_loop(),
                name=f"call_{chat_id}",
            )

            logger.info("Qo'ng'iroq qabul qilindi: chat_id={}", chat_id)

        except Exception as e:
            logger.error("Qo'ng'iroqni qabul qilishda xato: {}", e)
            self._active_calls.pop(chat_id, None)

    async def end_call(self, chat_id: int) -> None:
        """Faol qo'ng'iroqni tugatadi.

        Args:
            chat_id: Tugatilishi kerak bo'lgan qo'ng'iroqning chat_id si.
        """
        state = self._active_calls.pop(chat_id, None)
        if state is None:
            logger.debug("chat_id={} uchun faol qo'ng'iroq topilmadi", chat_id)
            return

        state.status = "ended"

        # Suhbat tsiklini to'xtatish
        if state._task and not state._task.done():
            state._task.cancel()
            try:
                await state._task
            except asyncio.CancelledError:
                pass

        # Qo'ng'iroqni tugatish
        # ⚠️  pytgcalls API versiyasiga bog'liq
        if self._tgcalls:
            try:
                await self._tgcalls.leave_call(chat_id)  # type: ignore
            except Exception as e:
                logger.warning("Qo'ng'iroqni tugatishda xato: {}", e)

        logger.info("Qo'ng'iroq tugatildi: chat_id={}", chat_id)

    # ----- Ichki hodisa qayta ishlash -----

    async def _on_raw_update(self, update: TgCallUpdate) -> None:
        """pytgcalls dan kelgan xom hodisani qayta ishlaydi.

        ⚠️  pytgcalls ichki API — barqaror emas.
        """
        logger.debug("TgCalls hodisa: {}", type(update).__name__)

        # Kiruvchi qo'ng'iroqni aniqlash va qabul qilish
        # Bu yerda pytgcalls versiyasiga qarab turli hodisa turlari
        # bo'lishi mumkin.
        try:
            await self.handle_incoming_call(update)
        except Exception as e:
            logger.error("Hodisa qayta ishlashda xato: {}", e)

    # ----- Statistika -----

    @property
    def active_call_count(self) -> int:
        """Faol qo'ng'iroqlar soni."""
        return len(self._active_calls)

    def is_in_call(self, chat_id: int) -> bool:
        """Berilgan chat_id uchun faol qo'ng'iroq borligini tekshiradi."""
        return chat_id in self._active_calls
