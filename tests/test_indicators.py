"""Tests básicos para los indicadores técnicos."""

import pandas as pd
import pytest

from strategy.indicators import atr, ema, rsi, sma


def test_sma_returns_expected_value() -> None:
    series = pd.Series([1.0, 2.0, 3.0])
    result = sma(series, 2)
    assert result.iloc[-1] == pytest.approx(2.5)


def test_ema_preserves_length() -> None:
    series = pd.Series([1.0, 2.0, 3.0, 4.0])
    assert len(ema(series, 2)) == len(series)


def test_rsi_is_bounded() -> None:
    series = pd.Series([1, 2, 3, 2, 3, 4, 3, 4], dtype=float)
    result = rsi(series, 3).dropna()
    assert ((result >= 0) & (result <= 100)).all()


def test_atr_requires_ohlc_columns() -> None:
    df = pd.DataFrame({"close": [1.0, 1.1]})
    with pytest.raises(ValueError):
        atr(df, 2)
