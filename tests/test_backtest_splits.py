"""Pruebas de partición temporal."""

import pandas as pd
import pytest

from backtesting.splits import chronological_split


def _data(rows: int = 10) -> pd.DataFrame:
    close = pd.Series(range(100, 100 + rows), dtype=float)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="h"),
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
        }
    )


def test_chronological_split_preserves_order_and_boundary() -> None:
    data = _data()
    train, test = chronological_split(data, 0.7)

    assert len(train) == 7
    assert len(test) == 3
    assert train.iloc[-1]["time"] < test.iloc[0]["time"]
    assert train.iloc[0]["time"] == pd.Timestamp(data.iloc[0]["time"], tz="UTC")
    assert test.iloc[-1]["time"] == pd.Timestamp(data.iloc[-1]["time"], tz="UTC")


@pytest.mark.parametrize("ratio", [0, 1, -0.1, 1.1])
def test_chronological_split_rejects_invalid_ratio(ratio: float) -> None:
    with pytest.raises(ValueError):
        chronological_split(_data(), ratio)


def test_chronological_split_rejects_duplicate_timestamps() -> None:
    df = _data()
    df.loc[5, "time"] = df.loc[4, "time"]

    with pytest.raises(ValueError, match="duplicados"):
        chronological_split(df)


def test_chronological_split_rejects_invalid_prices() -> None:
    df = _data()
    df.loc[3, "close"] = float("nan")

    with pytest.raises(ValueError, match="precios inválidos"):
        chronological_split(df)


def test_chronological_split_does_not_modify_input() -> None:
    df = _data()
    original = df.copy(deep=True)

    chronological_split(df)

    pd.testing.assert_frame_equal(df, original)
