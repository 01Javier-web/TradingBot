"""Serialización del gate de revisión humana de investigación."""

from __future__ import annotations

from typing import Any

from ai.research_decision import ResearchDecision


def decision_to_dict(decision: ResearchDecision) -> dict[str, Any]:
    """Convierte la decisión descriptiva en una estructura auditable."""
    return {
        "review_required": decision.review_required,
        "reasons": list(decision.reasons),
        "execution_authorized": False,
        "mode": "simulation-first",
    }
