"""Qadirdon AI — Markaziy AI Dvigateli (Google Gemini API)."""

from __future__ import annotations

import asyncio
from typing import Any
from google import genai
from google.genai import types
from loguru import logger

from config.settings import settings
from ai.prompts.personality import get_full_system_prompt
from ai.humanizer.style_adapter import humanize


class AiEngine:
    """Gemini 2.0 orqali insondek javob generatsiya qiluvchi sinf."""

    def __init__(self) -> None:
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GEMINI_API_KEY topilmadi, AI javoblari simulyatsiya rejimida ishlaydi.")

    async def generate_response(
        self,
        user_message: str,
        conversation_history: list[dict],
        ai_profile: Any,
        contact_name: str = "",
    ) -> dict[str, Any]:
        """
        AI javob yaratadi va uni insonlashtiradi.
        Returns:
            {
                "text": str,
                "correction": str | None,
                "parts": list[str],
                "delay_seconds": float
            }
        """
        system_instruction = get_full_system_prompt(
            role=getattr(ai_profile, "role", "aka"),
            ai_name=getattr(ai_profile, "ai_name", "Qadirdon"),
            personality_prompt=getattr(ai_profile, "personality_prompt", ""),
            language="uz",
            emoji_level=getattr(ai_profile, "emoji_level", 2),
            custom_phrases=getattr(ai_profile, "custom_phrases", None),
            relationship_level=getattr(ai_profile, "relationship_level", 1) or 1,
            game_mode=getattr(ai_profile, "game_mode", "story") or "story",
            character_id=getattr(ai_profile, "character_id", None),
        )

        if contact_name:
            system_instruction += f"\nSuhbatdoshingning ismi: {contact_name}."

        raw_text = await self._call_gemini(
            system_instruction=system_instruction,
            conversation_history=conversation_history,
            user_message=user_message,
        )

        # Insoniylashtirish (slang, typo, emoji)
        humanized_text, correction = humanize(raw_text, ai_profile)

        # Xabarlarni qismlarga bo'lish (agar uzun bo'lsa)
        parts = self._split_messages(humanized_text, getattr(ai_profile, "message_splitting", True))

        # Yozish kechikish vaqti
        speed = getattr(ai_profile, "typing_speed", 2)
        delay = self._calculate_delay(len(humanized_text), speed)

        return {
            "text": humanized_text,
            "correction": correction,
            "parts": parts,
            "delay_seconds": delay,
        }

    async def _call_gemini(
        self,
        system_instruction: str,
        conversation_history: list[dict],
        user_message: str,
    ) -> str:
        if not self.client:
            # Test / Offline rejim
            await asyncio.sleep(0.5)
            return "Salom! Men hozir offline test rejimdaman, API kalit sozlanmagan."

        try:
            contents = self._prepare_gemini_contents(conversation_history, user_message)

            # Gemini API orqali chaqirish (avtomatik fallback bilan)
            candidate_models = [
                getattr(settings, "GEMINI_MODEL", "gemini-3.1-flash-lite"),
                "gemini-3.5-flash-lite",
                "gemini-3.8-flash",
            ]
            last_error = None
            for model_name in candidate_models:
                try:
                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.85,
                            max_output_tokens=300,
                        ),
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as model_err:
                    last_error = model_err
                    logger.warning(f"Model {model_name} xatosi: {model_err}, keyingi modelga o'tilmoqda...")

            raise last_error or RuntimeError("Barcha Gemini modellari muvaffaqiyatsiz bo'ldi")
        except Exception as e:
            logger.error(f"Gemini API xatolik: {e}")
            return "Hozir ozroq band edim, nima deding?"

    def _prepare_gemini_contents(
        self,
        conversation_history: list[dict],
        user_message: str,
    ) -> list[types.Content]:
        """Gemini API uchun xabarlar ketma-ketligini tayyorlaydi.
        
        - Duplikatsiyaning oldini oladi.
        - Ketma-ket bir xil rollarni bitta turnga birlashtiradi (strict alternation).
        - Bo'sh qismlarni filtrlaydi.
        """
        raw_turns: list[dict[str, str]] = []
        for msg in conversation_history:
            content = (msg.get("content") or "").strip()
            if not content:
                continue
            role = "user" if msg.get("role") == "user" else "model"
            raw_turns.append({"role": role, "content": content})

        clean_user_msg = (user_message or "").strip()
        if clean_user_msg:
            if not raw_turns or raw_turns[-1]["content"] != clean_user_msg or raw_turns[-1]["role"] != "user":
                raw_turns.append({"role": "user", "content": clean_user_msg})

        if not raw_turns:
            return [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=clean_user_msg or "Salom")]
                )
            ]

        # Ketma-ket bir xil rollarni birlashtirish
        merged_turns: list[dict[str, str]] = []
        for turn in raw_turns:
            if merged_turns and merged_turns[-1]["role"] == turn["role"]:
                merged_turns[-1]["content"] += f"\n{turn['content']}"
            else:
                merged_turns.append(dict(turn))

        return [
            types.Content(
                role=turn["role"],
                parts=[types.Part.from_text(text=turn["content"])]
            )
            for turn in merged_turns
        ]

    def _split_messages(self, text: str, allow_split: bool) -> list[str]:
        if not allow_split or len(text) < 120 or "\n" not in text:
            return [text]

        parts = [p.strip() for p in text.split("\n") if p.strip()]
        return parts if parts else [text]

    def _calculate_delay(self, text_length: int, speed: int) -> float:
        if speed == 3:
            return 0.0
        if speed == 2:
            return min(1.0, max(0.2, text_length * 0.015))
        return min(2.0, max(0.5, text_length * 0.03))


ai_engine = AiEngine()
