"""Capa de investigación de estrategias, sin autoridad de ejecución.

El investigador transforma resultados de experimentos en observaciones
estructuradas. No modifica configuraciones de riesgo ni ejecuta operaciones.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from backtesting.optimizer import OptimizationResult


@dataclass(frozen=True)
class ResearchFinding:
    """Observación reproducible sobre un conjunto de resultados."""

    experiments: int
    profitable_train: int
    profitable_test: int
    generalization_rate: float
    findings: tuple[str, ...]


def summarize_optimization(results: list[OptimizationResult]) -> ResearchFinding:
    """Resume resultados train/test sin seleccionar una operación ni ejecutarla."""
    if not results:
        return ResearchFinding(0, 0, 0, 0.0, ("No hay resultados para analizar.",))

    train_positive = sum(result.train_pnl > 0 for result in results)
    test_positive = sum(result.test_pnl > 0 for result in results)
    generalizing = sum(result.train_pnl > 0 and result.test_pnl > 0 for result in results)
    rate = generalizing / len(results)

    findings = (
        f"Experimentos evaluados: {len(results)}.",
        f"Resultados con PnL positivo en train: {train_positive}.",
        f"Resultados con PnL positivo en test: {test_positive}.",
        f"Generalización positiva train+test: {rate:.1%}.",
    )
    if not isfinite(rate):
        raise ValueError("La tasa de generalización no es finita")

    return ResearchFinding(
        experiments=len(results),
        profitable_train=train_positive,
        profitable_test=test_positive,
        generalization_rate=rate,
        findings=findings,
    )
