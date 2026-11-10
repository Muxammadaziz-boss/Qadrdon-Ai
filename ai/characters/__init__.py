"""Qadirdon AI — Barcha rollar uchun personaj modellari registri."""

from __future__ import annotations
from typing import Any

from ai.characters.qiz_dost_models import QIZ_DOST_MODELS
from ai.characters.ayol_models import AYOL_MODELS
from ai.characters.ona_models import ONA_MODELS
from ai.characters.aka_models import AKA_MODELS
from ai.characters.uka_models import UKA_MODELS
from ai.characters.opa_models import OPA_MODELS
from ai.characters.singil_models import SINGIL_MODELS

ALL_MODELS: dict[str, dict[str, dict[str, Any]]] = {
    "qiz_dost": QIZ_DOST_MODELS,
    "ayol": AYOL_MODELS,
    "ona": ONA_MODELS,
    "aka": AKA_MODELS,
    "uka": UKA_MODELS,
    "opa": OPA_MODELS,
    "singil": SINGIL_MODELS,
}


def get_character_model(role: str, character_id: str | None) -> dict[str, Any] | None:
    """Rol va model ID si bo'yicha personaj modelini qaytaradi."""
    if not character_id or role not in ALL_MODELS:
        return None
    return ALL_MODELS[role].get(character_id)


def list_character_models(role: str) -> dict[str, dict[str, Any]]:
    """Berilgan rol uchun mavjud barcha modellarni qaytaradi."""
    return ALL_MODELS.get(role, {})
