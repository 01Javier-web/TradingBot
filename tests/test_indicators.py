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


def test_indicators_do_not_change_when_future_rows_are_appended() -> None:
    base = pd.DataFrame(
        {
            "high": [102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0],
            "close": [101.0, 102.0, 103.0],
        }
    )
    future = pd.DataFrame(
        {
            "high": [150.0, 200.0],
            "low": [50.0, 25.0],
            "close": [120.0, 180.0],
        }
    )

    from strategy.signals import StrategyConfig, add_indicators

    config = StrategyConfig(
        fast_ema_period=2,
        slow_ema_period=3,
        rsi_period=2,
        atr_period=2,
    )
    base_result = add_indicators(base, config)
    extended_result = add_indicators(pd.concat([base, future], ignore_index=True), config)

    pd.testing.assert_series_equal(
        base_result["ema_fast"],
        extended_result["ema_fast"].iloc[: len(base)].reset_index(drop=True),
        check_names=False,
    )
    pd.testing.assert_series_equal(
        base_result["ema_slow"],
        extended_result["ema_slow"].iloc[: len(base)].reset_index(drop=True),
        check_names=False,
    )
    pd.testing.assert_series_equal(
        base_result["rsi"],
        extended_result["rsi"].iloc[: len(base)].reset_index(drop=True),
        check_names=False,
    )
    pd.testing.assert_series_equal(
        base_result["atr"],
        extended_result["atr"].iloc[: len(base)].reset_index(drop=True),
        check_names=False,
    )
