"""Pruebas de normalización de datos de mercado de MT5."""

import numpy as np
import pandas as pd
import pytest

from data.mt5_normalizer import normalize_market_rates


def _rates() -> np.ndarray:
    rates = np.zeros(
        3,
        dtype=[
            ("time", "i8"),
            ("open", "f8"),
            ("high", "f8"),
            ("low", "f8"),
            ("close", "f8"),
            ("tick_volume", "i8"),
        ],
    )
    rates["time"] = [1767225600, 1767226500, 1767227400]
    rates["open"] = [100, 101, 102]
    rates["high"] = [101, 102, 103]
    rates["low"] = [99, 100, 101]
    rates["close"] = [100.5, 101.5, 102.5]
    rates["tick_volume"] = [10, 11, 12]
    return rates


def test_normalizer_converts_mt5_epoch_and_keeps_ohlc() -> None:
    result = normalize_market_rates(_rates())

    assert list(result.columns) == ["time", "open", "high", "low", "close"]
    assert str(result["time"].dt.tz) == "UTC"
    assert result["time"].is_monotonic_increasing
    assert result["close"].tolist() == [100.5, 101.5, 102.5]


def test_normalizer_rejects_missing_market_columns() -> None:
    with pytest.raises(ValueError, match="Faltan columnas de mercado"):
        normalize_market_rates(pd.DataFrame({"time": [1], "close": [100]}))


def test_normalizer_rejects_invalid_ohlc() -> None:
    rates = _rates()
    rates["high"][1] = 0

    with pytest.raises(ValueError, match="mayores que 0"):
        normalize_market_rates(rates)


def test_normalizer_does_not_require_tick_volume() -> None:
    result = normalize_market_rates(
        pd.DataFrame(
            {
                "time": pd.date_range("2026-01-01", periods=2, freq="15min", tz="UTC"),
                "open": [10.0, 11.0],
                "high": [11.0, 12.0],
                "low": [9.0, 10.0],
                "close": [10.5, 11.5],
            }
        )
    )

    assert len(result) == 2
