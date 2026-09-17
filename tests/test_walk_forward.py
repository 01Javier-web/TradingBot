"""Pruebas de validación walk-forward."""

import pandas as pd
import pytest

from backtesting.walk_forward import walk_forward
from strategy.signals import StrategyConfig


def make_data() -> pd.DataFrame:
    close = [100 + i * 0.1 for i in range(40)]
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=40, freq="15min"),
            "open": close,
            "high": [x + 0.1 for x in close],
            "low": [x - 0.1 for x in close],
            "close": close,
        }
    )


def test_walk_forward_creates_consecutive_windows() -> None:
    windows = walk_forward(make_data(), StrategyConfig(fast_ema_period=3, slow_ema_period=6), 20, 5)
    assert len(windows) == 4
    assert windows[0].train_end < windows[0].test_start
    assert windows[0].test_end < windows[1].test_start


def test_walk_forward_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError):
        walk_forward(make_data(), StrategyConfig(), 0, 5)
