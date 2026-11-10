"""Qadirdon AI — Rollar registri."""

from ai.prompts.roles import aka, ayol, ona, opa, qiz_dost, singil, uka

ROLES = {
    "aka": aka,
    "uka": uka,
    "opa": opa,
    "singil": singil,
    "ona": ona,
    "qiz_dost": qiz_dost,
    "ayol": ayol,
}

ROLE_NAMES_UZ = {
    "aka": "👨 Aka",
    "uka": "👦 Uka",
    "opa": "👩 Opa",
    "singil": "👧 Singil",
    "ona": "🤱 Ona",
    "qiz_dost": "💕 Qiz do'st",
    "ayol": "💍 Ayol / Turmush o'rtog'i",
}

__all__ = ["ROLES", "ROLE_NAMES_UZ"]
