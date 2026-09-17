"""Evaluación descriptiva de calidad para resultados de investigación."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from backtesting.optimizer import OptimizationResult


@dataclass(frozen=True)
class ResearchQuality:
    """Señales de calidad, sin seleccionar una configuración operativa."""

    sample_size: int
    finite_results: bool
    positive_train: int
    positive_test: int
    positive_both: int
    generalization_rate: float


def assess_quality(results: list[OptimizationResult]) -> ResearchQuality:
    """Resume cobertura y consistencia train/test de una investigación."""
    finite = all(isfinite(item.train_pnl) and isfinite(item.test_pnl) for item in results)
    positive_train = sum(item.train_pnl > 0 for item in results)
    positive_test = sum(item.test_pnl > 0 for item in results)
    positive_both = sum(item.train_pnl > 0 and item.test_pnl > 0 for item in results)
    rate = positive_both / len(results) if results else 0.0
    return ResearchQuality(
        sample_size=len(results),
        finite_results=finite,
        positive_train=positive_train,
        positive_test=positive_test,
        positive_both=positive_both,
        generalization_rate=rate,
    )
