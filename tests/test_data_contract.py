"""Pruebas del contrato mínimo de datos de mercado."""

import pandas as pd
import pytest

from data.loader import validate_market_data


def test_extra_columns_are_preserved() -> None:
    df = pd.DataFrame(
        {
            "time": ["2026-01-01 00:00"],
            "open": [100],
            "high": [101],
            "low": [99],
            "close": [100.5],
            "tick_volume": [123],
        }
    )

    result = validate_market_data(df)

    assert "tick_volume" in result.columns


def test_validation_does_not_mutate_input() -> None:
    df = pd.DataFrame(
        {
            "time": ["2026-01-01 00:00"],
            "open": [100],
            "high": [101],
            "low": [99],
            "close": [100.5],
        }
    )
    original = df.copy(deep=True)

    validate_market_data(df)

    pd.testing.assert_frame_equal(df, original)


def test_numeric_nan_is_rejected() -> None:
    df = pd.DataFrame(
        {
            "time": ["2026-01-01 00:00"],
            "open": [100],
            "high": [101],
            "low": [99],
            "close": [float("nan")],
        }
    )

    with pytest.raises(ValueError, match="precios contienen"):
        validate_market_data(df)
