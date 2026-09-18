"""Validaciones mínimas para resultados de investigación.

Esta capa detecta resultados incompletos o no comparables antes de que puedan
usarse como evidencia de una estrategia. No decide qué configuración operar.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from backtesting.optimizer import OptimizationResult


@dataclass(frozen=True)
class ResearchValidation:
    """Estado de calidad de una corrida de investigación."""

    valid: bool
    issues: tuple[str, ...]


def validate_results(results: list[OptimizationResult]) -> ResearchValidation:
    """Comprueba que los resultados tengan PnL finitos y configuraciones únicas."""
    issues: list[str] = []

    if not isinstance(results, list):
        return ResearchValidation(False, ("results debe ser una lista.",))

    if any(not isinstance(result, OptimizationResult) for result in results):
        return ResearchValidation(False, ("Todos los resultados deben ser OptimizationResult.",))

    if not results:
        issues.append("No hay resultados de optimización.")

    configs = [result.config for result in results]
    if len(configs) != len(set(configs)):
        issues.append("Hay configuraciones duplicadas.")

    for index, result in enumerate(results, start=1):
        if not isfinite(result.train_pnl):
            issues.append(f"Resultado {index}: train_pnl no es finito.")
        if not isfinite(result.test_pnl):
            issues.append(f"Resultado {index}: test_pnl no es finito.")

    return ResearchValidation(valid=not issues, issues=tuple(issues))
