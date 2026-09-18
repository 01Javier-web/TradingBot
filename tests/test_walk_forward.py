"""Pruebas de validación walk-forward."""

import pandas as pd
import pytest

from backtesting.walk_forward import walk_forward
from strategy.signals import StrategyConfig


def make_data(rows: int = 40) -> pd.DataFrame:
    close = [100 + i * 0.1 for i in range(rows)]
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="15min"),
            "open": close,
            "high": [x + 0.1 for x in close],
            "low": [x - 0.1 for x in close],
            "close": close,
        }
    )


def test_walk_forward_creates_consecutive_windows() -> None:
    windows = walk_forward(
        make_data(),
        StrategyConfig(fast_ema_period=3, slow_ema_period=6),
        20,
        5,
    )
    assert len(windows) == 4
    assert windows[0].train_end < windows[0].test_start
    assert windows[0].test_end < windows[1].test_start


def test_walk_forward_returns_no_windows_when_data_is_too_short() -> None:
    assert walk_forward(make_data(10), StrategyConfig(), 8, 5) == ()


def test_walk_forward_rejects_invalid_sizes() -> None:
    with pytest.raises(ValueError):
        walk_forward(make_data(), StrategyConfig(), 0, 5)
    with pytest.raises(ValueError):
        walk_forward(make_data(), StrategyConfig(), 5, 0)
    with pytest.raises(ValueError):
        walk_forward(make_data(), StrategyConfig(), 5, 5, step=0)


def test_walk_forward_rejects_duplicate_timestamps() -> None:
    df = make_data()
    df.loc[10, "time"] = df.loc[9, "time"]

    with pytest.raises(ValueError, match="duplicados"):
        walk_forward(df, StrategyConfig(), 20, 5)


def test_walk_forward_rejects_invalid_market_prices() -> None:
    df = make_data()
    df.loc[10, "close"] = float("inf")

    with pytest.raises(ValueError, match="infinitos"):
        walk_forward(df, StrategyConfig(), 20, 5)
