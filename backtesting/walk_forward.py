"""Validación walk-forward para evaluar estabilidad temporal."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import pandas as pd

from backtesting.engine import BacktestEngine
from backtesting.walk_forward_validation import validate_walk_forward
from data.quality import validate_time_series
from strategy.signals import StrategyConfig


@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: object
    train_end: object
    test_start: object
    test_end: object
    test_pnl: float


def walk_forward(
    df: pd.DataFrame,
    config: StrategyConfig,
    train_size: int,
    test_size: int,
    step: int | None = None,
) -> tuple[WalkForwardWindow, ...]:
    """Evalúa una configuración fija sobre ventanas test cronológicas.

    El tramo train se conserva como contexto temporal y no se usa para ajustar
    parámetros. Esta función es una evaluación temporal walk-forward de una
    configuración ya definida, no un optimizador walk-forward automático.
    """
    sizes = (train_size, test_size)
    if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in sizes):
        raise ValueError("train_size y test_size deben ser enteros mayores que 0")
    if step is None:
        step = test_size
    if isinstance(step, bool) or not isinstance(step, int) or step <= 0:
        raise ValueError("step debe ser un entero mayor que 0")

    data = validate_time_series(df)
    if len(data) < train_size + test_size:
        return ()

    windows: list[WalkForwardWindow] = []
    engine = BacktestEngine()
    start = 0
    while start + train_size + test_size <= len(data):
        train = data.iloc[start : start + train_size]
        test = data.iloc[start + train_size : start + train_size + test_size]

        result = engine.run(test, config)
        windows.append(
            WalkForwardWindow(
                train_start=train.iloc[0]["time"],
                train_end=train.iloc[-1]["time"],
                test_start=test.iloc[0]["time"],
                test_end=test.iloc[-1]["time"],
                test_pnl=float(result.net_pnl),
            )
        )
        start += step

    validated = validate_walk_forward(tuple(windows))
    if not validated.valid:
        raise ValueError("Walk-forward inválido: " + " ".join(validated.issues))
    if any(not isfinite(window.test_pnl) for window in windows):
        raise ValueError("El PnL walk-forward debe ser finito")
    return tuple(windows)
