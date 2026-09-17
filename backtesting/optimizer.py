"""Búsqueda controlada de parámetros para investigación de estrategias."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import pandas as pd

from backtesting.engine import BacktestEngine
from backtesting.splits import chronological_split
from strategy.signals import StrategyConfig


@dataclass(frozen=True)
class ParameterGrid:
    """Valores explícitos que se pueden explorar."""

    fast_ema_periods: tuple[int, ...] = (10, 20, 30)
    slow_ema_periods: tuple[int, ...] = (40, 50, 60)
    rsi_periods: tuple[int, ...] = (14,)


@dataclass(frozen=True)
class OptimizationResult:
    config: StrategyConfig
    train_pnl: float
    test_pnl: float


def optimize(df: pd.DataFrame, grid: ParameterGrid, train_ratio: float = 0.7) -> list[OptimizationResult]:
    """Evalúa combinaciones en train y las contrasta en test cronológico.

    No ordena por test_pnl: el objetivo es conservar los resultados para que la
    selección final pueda hacerse con criterios de validación definidos aparte.
    """
    train, test = chronological_split(df, train_ratio)
    results: list[OptimizationResult] = []
    for fast, slow, rsi_period in product(
        grid.fast_ema_periods, grid.slow_ema_periods, grid.rsi_periods
    ):
        if fast >= slow:
            continue
        config = StrategyConfig(fast_ema_period=fast, slow_ema_period=slow, rsi_period=rsi_period)
        engine = BacktestEngine()
        train_result = engine.run(train, config)
        test_result = engine.run(test, config)
        results.append(
            OptimizationResult(
                config=config,
                train_pnl=train_result.net_pnl,
                test_pnl=test_result.net_pnl,
            )
        )
    return results
