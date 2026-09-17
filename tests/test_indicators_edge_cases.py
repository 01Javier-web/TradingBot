"""Casos límite para indicadores técnicos."""

import pandas as pd
import pytest

from strategy.indicators import ema, rsi, sma


def test_sma_rejects_non_positive_period() -> None:
    with pytest.raises(ValueError):
        sma(pd.Series([1.0, 2.0]), 0)


def test_ema_rejects_boolean_period() -> None:
    with pytest.raises(ValueError):
        ema(pd.Series([1.0, 2.0]), True)


def test_rsi_stays_at_100_when_prices_only_rise() -> None:
    result = rsi(pd.Series([1, 2, 3, 4, 5], dtype=float), period=3)

    assert result.iloc[-1] == pytest.approx(100.0)


def test_rsi_stays_at_50_when_prices_are_constant() -> None:
    result = rsi(pd.Series([10, 10, 10, 10], dtype=float), period=2)

    assert result.iloc[-1] == pytest.approx(50.0)
