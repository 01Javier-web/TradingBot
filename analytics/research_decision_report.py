"""Serialización del gate de revisión humana de investigación."""

from __future__ import annotations

from typing import Any

from ai.research_decision import ResearchDecision


def decision_to_dict(decision: ResearchDecision) -> dict[str, Any]:
    """Convierte la decisión descriptiva en una estructura auditable."""
    if not isinstance(decision, ResearchDecision):
        raise ValueError("decision debe ser ResearchDecision")
    if not isinstance(decision.review_required, bool):
        raise ValueError("review_required debe ser booleano")
    if not isinstance(decision.reasons, tuple) or any(not isinstance(reason, str) for reason in decision.reasons):
        raise ValueError("reasons debe ser una tupla de texto")
    return {
        "review_required": decision.review_required,
        "reasons": list(decision.reasons),
        "execution_authorized": False,
        "mode": "simulation-first",
    }
