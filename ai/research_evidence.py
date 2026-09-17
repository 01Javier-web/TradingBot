"""Construcción de evidencia para una corrida de investigación.

Este módulo reúne validación, clasificación y hallazgos sin tomar decisiones
operativas. La salida está pensada para revisión humana y auditoría.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai.research_selection import ResearchCandidate, classify_consistency
from ai.research_validation import ResearchValidation, validate_results
from backtesting.optimizer import OptimizationResult


@dataclass(frozen=True)
class ResearchEvidence:
    """Paquete de evidencia generado a partir de resultados."""

    validation: ResearchValidation
    candidates: tuple[ResearchCandidate, ...]


def build_evidence(results: list[OptimizationResult]) -> ResearchEvidence:
    """Valida y clasifica resultados manteniendo trazabilidad de entrada."""
    validation = validate_results(results)
    candidates = classify_consistency(results) if validation.valid else ()
    return ResearchEvidence(validation=validation, candidates=candidates)
