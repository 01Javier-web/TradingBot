"""Selección descriptiva de candidatos de investigación.

La función de este módulo es ordenar evidencia para inspección humana. No
convierte el resultado en una orden ni modifica los límites de riesgo.
"""

from __future__ import annotations

from dataclasses import dataclass

from backtesting.optimizer import OptimizationResult


@dataclass(frozen=True)
class ResearchCandidate:
    """Candidato acompañado de una medida simple de consistencia."""

    result: OptimizationResult
    consistent: bool


def classify_consistency(results: list[OptimizationResult]) -> tuple[ResearchCandidate, ...]:
    """Clasifica resultados según PnL positivo tanto en train como en test.

    El orden original se conserva deliberadamente para evitar introducir una
    clasificación implícita por rentabilidad.
    """
    if not isinstance(results, list):
        raise ValueError("results debe ser una lista")
    if any(not isinstance(result, OptimizationResult) for result in results):
        raise ValueError("Todos los resultados deben ser OptimizationResult")
    return tuple(
        ResearchCandidate(
            result=result,
            consistent=result.train_pnl > 0 and result.test_pnl > 0,
        )
        for result in results
    )
