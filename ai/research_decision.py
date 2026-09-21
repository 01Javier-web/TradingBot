"""Puente de investigación hacia revisión humana, sin autoridad operativa."""

from __future__ import annotations

from dataclasses import dataclass

from ai.research_pipeline import ResearchRun
from backtesting.walk_forward_validation import WalkForwardValidation
from ai.research_gate import FinalValidation


@dataclass(frozen=True)
class ResearchDecision:
    """Estado descriptivo para decidir si una investigación requiere revisión."""

    review_required: bool
    reasons: tuple[str, ...]


def build_research_decision(
    run: ResearchRun,
    walk_forward_validation: WalkForwardValidation | None = None,
    final_validation: FinalValidation | None = None,
) -> ResearchDecision:
    """Marca condiciones que requieren revisión sin recomendar operaciones."""
    if not isinstance(run, ResearchRun):
        raise ValueError("run debe ser ResearchRun")
    if walk_forward_validation is not None and not isinstance(walk_forward_validation, WalkForwardValidation):
        raise ValueError("walk_forward_validation debe ser WalkForwardValidation o None")
    if final_validation is not None and not isinstance(final_validation, FinalValidation):
        raise ValueError("final_validation debe ser FinalValidation o None")

    reasons: list[str] = []

    if not run.evidence.validation.valid:
        reasons.append("La evidencia de investigación contiene problemas de validación.")
    if not run.results:
        reasons.append("No existen resultados para revisar.")
    if not run.evidence.candidates:
        reasons.append("No hay candidatos consistentes train/test para revisar.")
    if walk_forward_validation is not None and not walk_forward_validation.valid:
        reasons.append("La validación walk-forward contiene problemas.")
    if final_validation is not None and not final_validation.valid:
        reasons.append("La validación final del candidato contiene problemas.")

    return ResearchDecision(review_required=bool(reasons), reasons=tuple(reasons))
