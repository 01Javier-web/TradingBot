"""Pruebas de separación temporal train/test."""

import pandas as pd
import pytest

from backtesting.splits import chronological_split


def test_chronological_split_preserves_time_order() -> None:
    df = pd.DataFrame({"time": pd.date_range("2026-01-01", periods=10, freq="h"), "close": range(10)})
    train, test = chronological_split(df, 0.7)
    assert len(train) == 7
    assert len(test) == 3
    assert train["time"].max() < test["time"].min()


def test_split_rejects_unsorted_data() -> None:
    df = pd.DataFrame({"time": pd.to_datetime(["2026-01-02", "2026-01-01"]), "close": [2, 1]})
    with pytest.raises(ValueError):
        chronological_split(df)
