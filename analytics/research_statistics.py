"""Diagnósticos estadísticos descriptivos para investigación.

Este módulo no selecciona estrategias ni autoriza ejecución. Solo transforma
las métricas producidas por backtesting en señales de calidad auditables.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from statistics import median

from backtesting.optimizer import OptimizationResult


@dataclass(frozen=True)
class ResearchStatisticsConfig:
    """Umbrales explícitos para diagnósticos, no para decidir rentabilidad."""

    minimum_test_trades: int = 30
    maximum_test_drawdown: float = 0.25
    minimum_test_to_train_pnl_ratio: float = 0.25

    def __post_init__(self) -> None:
        if (
            isinstance(self.minimum_test_trades, bool)
            or not isinstance(self.minimum_test_trades, int)
            or self.minimum_test_trades < 0
        ):
            raise ValueError("minimum_test_trades debe ser un entero no negativo")
        if (
            isinstance(self.maximum_test_drawdown, bool)
            or not isinstance(self.maximum_test_drawdown, (int, float))
            or not isfinite(float(self.maximum_test_drawdown))
            or self.maximum_test_drawdown < 0
        ):
            raise ValueError("maximum_test_drawdown debe ser finito y no negativo")
        if (
            isinstance(self.minimum_test_to_train_pnl_ratio, bool)
            or not isinstance(self.minimum_test_to_train_pnl_ratio, (int, float))
            or not isfinite(float(self.minimum_test_to_train_pnl_ratio))
            or self.minimum_test_to_train_pnl_ratio < 0
        ):
            raise ValueError("minimum_test_to_train_pnl_ratio debe ser finito y no negativo")


@dataclass(frozen=True)
class ResearchStatistics:
    """Resumen descriptivo de robustez estadística."""

    results: int
    metrics_available: int
    insufficient_test_sample: int
    high_test_drawdown: int
    train_positive_test_negative: int
    weak_test_generalization: int
    median_test_trades: float
    median_test_drawdown: float
    median_test_win_rate: float
    median_test_profit_factor: float | None
    parameter_variants: int
    warnings: tuple[str, ...]

    @property
    def statistically_incomplete(self) -> bool:
        """Indica si faltan métricas de backtest para una evaluación estadística completa."""
        return self.metrics_available < self.results


def assess_statistics(
    results: list[OptimizationResult],
    config: ResearchStatisticsConfig | None = None,
) -> ResearchStatistics:
    """Calcula diagnósticos sin ordenar ni seleccionar configuraciones."""
    if not isinstance(results, list):
        raise ValueError("results debe ser una lista")
    if any(not isinstance(item, OptimizationResult) for item in results):
        raise ValueError("Todos los resultados deben ser OptimizationResult")

    settings = config or ResearchStatisticsConfig()
    total = len(results)

    fully_measured = [
        item
        for item in results
        if item.test_trades is not None
        and item.test_drawdown is not None
        and item.test_win_rate is not None
        and item.test_profit_factor is not None
    ]

    insufficient = sum(
        item.test_trades is not None and item.test_trades < settings.minimum_test_trades
        for item in results
    )
    high_drawdown = sum(
        item.test_drawdown is not None and item.test_drawdown > settings.maximum_test_drawdown
        for item in results
    )
    train_positive_test_negative = sum(
        item.train_pnl > 0 and item.test_pnl <= 0 for item in results
    )

    weak_generalization = 0
    for item in results:
        if item.train_pnl <= 0 or item.test_pnl <= 0:
            continue
        ratio = item.test_pnl / item.train_pnl
        if ratio < settings.minimum_test_to_train_pnl_ratio:
            weak_generalization += 1

    test_trades = [item.test_trades for item in fully_measured if item.test_trades is not None]
    drawdowns = [item.test_drawdown for item in fully_measured if item.test_drawdown is not None]
    win_rates = [item.test_win_rate for item in fully_measured if item.test_win_rate is not None]
    profit_factors = [
        item.test_profit_factor
        for item in fully_measured
        if item.test_profit_factor is not None
    ]

    warnings: list[str] = []
    if total == 0:
        warnings.append("No hay resultados de optimización.")
    if total and len(fully_measured) < total:
        warnings.append("Faltan métricas de backtest en uno o más resultados.")
    if insufficient:
        warnings.append(
            f"{insufficient} resultado(s) tienen menos de "
            f"{settings.minimum_test_trades} operaciones en test."
        )
    if high_drawdown:
        warnings.append(
            f"{high_drawdown} resultado(s) superan el drawdown máximo configurado "
            f"de {settings.maximum_test_drawdown:.1%}."
        )
    if train_positive_test_negative:
        warnings.append(
            f"{train_positive_test_negative} resultado(s) son positivos en train y "
            "no positivos en test."
        )
    if weak_generalization:
        warnings.append(
            f"{weak_generalization} resultado(s) positivos presentan una relación "
            "test/train inferior al umbral configurado."
        )

    return ResearchStatistics(
        results=total,
        metrics_available=len(fully_measured),
        insufficient_test_sample=insufficient,
        high_test_drawdown=high_drawdown,
        train_positive_test_negative=train_positive_test_negative,
        weak_test_generalization=weak_generalization,
        median_test_trades=float(median(test_trades)) if test_trades else 0.0,
        median_test_drawdown=float(median(drawdowns)) if drawdowns else 0.0,
        median_test_win_rate=float(median(win_rates)) if win_rates else 0.0,
        median_test_profit_factor=float(median(profit_factors)) if profit_factors else None,
        parameter_variants=len({item.config for item in results}),
        warnings=tuple(warnings),
    )


__all__ = ["ResearchStatistics", "ResearchStatisticsConfig", "assess_statistics"]
