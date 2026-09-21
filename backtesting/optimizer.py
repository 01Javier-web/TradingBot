"""Búsqueda controlada de parámetros para investigación de estrategias."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite

import pandas as pd

from backtesting.engine import BacktestEngine
from backtesting.metrics import max_drawdown, profit_factor, win_rate
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
            if len(set(values)) != len(values):
                raise ValueError(f"{name} no puede contener valores duplicados")
            if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in values):
                raise ValueError(f"{name} debe contener enteros mayores que 0")
        if not any(fast < slow for fast in self.fast_ema_periods for slow in self.slow_ema_periods):
            raise ValueError("La cuadrícula no contiene combinaciones fast/slow válidas")


@dataclass(frozen=True)
class OptimizationResult:
    config: StrategyConfig
    train_pnl: float
    test_pnl: float
    train_trades: int | None = None
    test_trades: int | None = None
    train_drawdown: float | None = None
    test_drawdown: float | None = None
    train_win_rate: float | None = None
    test_win_rate: float | None = None
    train_profit_factor: float | None = None
    test_profit_factor: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.config, StrategyConfig):
            raise ValueError("config debe ser StrategyConfig")
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in (self.train_pnl, self.test_pnl)
        ):
            raise ValueError("train_pnl y test_pnl deben ser numéricos")
        if not all(isfinite(float(value)) for value in (self.train_pnl, self.test_pnl)):
            raise ValueError("train_pnl y test_pnl deben ser finitos")

        counts = (self.train_trades, self.test_trades)
        if any(value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0) for value in counts):
            raise ValueError("Los conteos de operaciones deben ser enteros no negativos o None")

        drawdowns = (self.train_drawdown, self.test_drawdown)
        if any(
            value is not None
            and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(float(value))
                or value < 0
            )
            for value in drawdowns
        ):
            raise ValueError("Los drawdowns deben ser finitos y no negativos o None")

        win_rates = (self.train_win_rate, self.test_win_rate)
        if any(
            value is not None
            and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(float(value))
                or not 0 <= float(value) <= 1
            )
            for value in win_rates
        ):
            raise ValueError("Los win rates deben estar entre 0 y 1 o ser None")

        profit_factors = (self.train_profit_factor, self.test_profit_factor)
        if any(
            value is not None
            and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(float(value))
                or value < 0
            )
            for value in profit_factors
        ):
            raise ValueError("Los profit factors deben ser finitos y no negativos o None")


def _finite_profit_factor(value: float) -> float | None:
    """Convierte un profit factor infinito en None para conservar JSON finito."""
    return float(value) if isfinite(float(value)) else None


def optimize(df: pd.DataFrame, grid: ParameterGrid, train_ratio: float = 0.7) -> list[OptimizationResult]:
    """Evalúa combinaciones en train y las contrasta en test cronológico.

    No ordena por test_pnl: el objetivo es conservar los resultados para que la
    selección final pueda hacerse con criterios de validación definidos aparte.
    """
    if not isinstance(grid, ParameterGrid):
        raise ValueError("grid debe ser ParameterGrid")
    if isinstance(train_ratio, bool) or not isinstance(train_ratio, (int, float)) or not isfinite(float(train_ratio)):
        raise ValueError("train_ratio debe ser numérico y finito")
    train, test = chronological_split(df, float(train_ratio))
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
        train_pnls = tuple(trade.net_pnl for trade in train_result.trades)
        test_pnls = tuple(trade.net_pnl for trade in test_result.trades)

        results.append(
            OptimizationResult(
                config=config,
                train_pnl=float(train_result.net_pnl),
                test_pnl=float(test_result.net_pnl),
                train_trades=len(train_result.trades),
                test_trades=len(test_result.trades),
                train_drawdown=float(max_drawdown(train_result.equity_curve)),
                test_drawdown=float(max_drawdown(test_result.equity_curve)),
                train_win_rate=float(win_rate(train_pnls)),
                test_win_rate=float(win_rate(test_pnls)),
                train_profit_factor=_finite_profit_factor(profit_factor(train_pnls)),
                test_profit_factor=_finite_profit_factor(profit_factor(test_pnls)),
            )
        )
    return results
