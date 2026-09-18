"""Pruebas de la frontera de validación del backtesting."""

from __future__ import annotations

import pandas as pd
import pytest

from backtesting.engine import BacktestEngine


def valid_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=3, freq="15min", tz="UTC"),
            "open": [100.0, 101.0, 102.0],
            "high": [102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0],
            "close": [101.0, 102.0, 103.0],
        }
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda df: df.iloc[::-1],
        lambda df: pd.concat([df, df.iloc[[0]]], ignore_index=True),
        lambda df: df.assign(close=[101.0, float("nan"), 103.0]),
        lambda df: df.assign(high=[98.0, 103.0, 104.0]),
        lambda df: df.assign(close=[101.0, 0.0, 103.0]),
    ],
)
def test_backtest_rejects_invalid_market_data(mutate) -> None:
    with pytest.raises(ValueError):
        BacktestEngine().run(mutate(valid_data()))


def test_backtest_accepts_valid_market_data() -> None:
    result = BacktestEngine().run(valid_data())

    assert result.initial_balance == pytest.approx(10_000.0)
    assert result.final_balance == pytest.approx(10_000.0)
