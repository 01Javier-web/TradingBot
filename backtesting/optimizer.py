"""Búsqueda controlada de parámetros para investigación de estrategias."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite

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

    def __post_init__(self) -> None:
        for name, values in (
            ("fast_ema_periods", self.fast_ema_periods),
            ("slow_ema_periods", self.slow_ema_periods),
            ("rsi_periods", self.rsi_periods),
        ):
            if not isinstance(values, tuple):
                raise ValueError(f"{name} debe ser tuple")
            if not values:
                raise ValueError(f"{name} no puede estar vacío")
            if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in values):
                raise ValueError(f"{name} debe contener enteros mayores que 0")
        if not any(fast < slow for fast in self.fast_ema_periods for slow in self.slow_ema_periods):
            raise ValueError("La cuadrícula no contiene combinaciones fast/slow válidas")


@dataclass(frozen=True)
class OptimizationResult:
    config: StrategyConfig
    train_pnl: float
    test_pnl: float

    def __post_init__(self) -> None:
        if not isinstance(self.config, StrategyConfig):
            raise ValueError("config debe ser StrategyConfig")
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in (self.train_pnl, self.test_pnl)
        ):
            raise ValueError("train_pnl y test_pnl deben ser numéricos")


def optimize(df: pd.DataFrame, grid: ParameterGrid, train_ratio: float = 0.7) -> list[OptimizationResult]:
    """Evalúa combinaciones en train y las contrasta en test cronológico.

    No ordena por test_pnl: el objetivo es conservar los resultados para que la
    selección final pueda hacerse con criterios de validación definidos aparte.
    """
    if not isinstance(grid, ParameterGrid):
        raise ValueError("grid debe ser ParameterGrid")
    train, test = chronological_split(df, train_ratio)
    results: list[OptimizationResult] = []
    seen: set[StrategyConfig] = set()

    for fast, slow, rsi_period in product(
        grid.fast_ema_periods, grid.slow_ema_periods, grid.rsi_periods
    ):
        if fast >= slow:
            continue
        config = StrategyConfig(fast_ema_period=fast, slow_ema_period=slow, rsi_period=rsi_period)
        if config in seen:
            continue
        seen.add(config)

        engine = BacktestEngine()
        train_result = engine.run(train, config)
        test_result = engine.run(test, config)
        results.append(
            OptimizationResult(
                config=config,
                train_pnl=float(train_result.net_pnl),
                test_pnl=float(test_result.net_pnl),
            )
        )
    return results
