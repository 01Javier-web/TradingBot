"""Validación walk-forward para evaluar estabilidad temporal."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtesting.engine import BacktestEngine
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
    """Ejecuta ventanas temporales consecutivas sin mezclar futuro y pasado."""
    if train_size <= 0 or test_size <= 0:
        raise ValueError("train_size y test_size deben ser mayores que 0")
    if step is None:
        step = test_size
    if step <= 0:
        raise ValueError("step debe ser mayor que 0")
    if "time" not in df.columns or not df["time"].is_monotonic_increasing:
        raise ValueError("Los datos deben estar ordenados temporalmente")

    windows: list[WalkForwardWindow] = []
    engine = BacktestEngine()
    start = 0
    while start + train_size + test_size <= len(df):
        train = df.iloc[start : start + train_size]
        test = df.iloc[start + train_size : start + train_size + test_size]
        result = engine.run(test, config)
        windows.append(
            WalkForwardWindow(
                train_start=train.iloc[0]["time"],
                train_end=train.iloc[-1]["time"],
                test_start=test.iloc[0]["time"],
                test_end=test.iloc[-1]["time"],
                test_pnl=result.net_pnl,
            )
        )
        start += step
    return tuple(windows)
