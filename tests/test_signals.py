"""Tests del motor de señales."""

import pandas as pd
import pytest

from strategy.signals import Signal, StrategyConfig, generate_signal, generate_signals


def test_generate_buy_signal() -> None:
    row = pd.Series({"ema_fast": 105.0, "ema_slow": 100.0, "rsi": 60.0, "atr": 2.0})
    assert generate_signal(row) == Signal.BUY


def test_generate_sell_signal() -> None:
    row = pd.Series({"ema_fast": 95.0, "ema_slow": 100.0, "rsi": 40.0, "atr": 2.0})
    assert generate_signal(row) == Signal.SELL


def test_generate_wait_for_insufficient_data() -> None:
    row = pd.Series({"ema_fast": 105.0, "ema_slow": 100.0, "rsi": float("nan"), "atr": 2.0})
    assert generate_signal(row) == Signal.WAIT


def test_generate_wait_when_atr_is_below_minimum() -> None:
    config = StrategyConfig(min_atr=1.0)
    row = pd.Series({"ema_fast": 105.0, "ema_slow": 100.0, "rsi": 60.0, "atr": 0.5})
    assert generate_signal(row, config) == Signal.WAIT


def test_generate_signals_adds_indicators_and_signal() -> None:
    rows = 80
    close = pd.Series(range(1, rows + 1), dtype=float)
    df = pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="h"),
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
        }
    )
    result = generate_signals(df)
    assert {"ema_fast", "ema_slow", "rsi", "atr", "signal"}.issubset(result.columns)
    assert result["signal"].iloc[-1] == Signal.BUY


def test_invalid_strategy_config() -> None:
    with pytest.raises(ValueError):
        StrategyConfig(fast_ema_period=50, slow_ema_period=20)


@pytest.mark.parametrize("kwargs", [
    {"rsi_buy_level": float("nan")},
    {"rsi_sell_level": float("inf")},
    {"min_atr": float("nan")},
])
def test_non_finite_strategy_config_is_rejected(kwargs: dict) -> None:
    with pytest.raises(ValueError, match="numéricos y finitos"):
        StrategyConfig(**kwargs)
