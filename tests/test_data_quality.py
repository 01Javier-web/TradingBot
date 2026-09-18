"""Pruebas de calidad de datos de mercado."""

from __future__ import annotations

import pandas as pd
import pytest

from data.quality import validate_time_series


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
        lambda df: df.assign(high=[98, 103, 104]),
        lambda df: df.assign(low=[101.5, 100, 101]),
        lambda df: df.assign(close=[100, 0, 103]),
        lambda df: df.assign(open=[100, float("nan"), 102]),
        lambda df: df.assign(close=[101, float("inf"), 103]),
    ],
)
def test_invalid_time_series_is_rejected(mutate) -> None:
    with pytest.raises(ValueError):
        validate_time_series(mutate(valid_data()))


def test_invalid_timestamp_is_rejected() -> None:
    df = pd.DataFrame(
        {
            "time": [
                "2026-01-01 00:00:00",
                "not-a-date",
                "2026-01-01 00:30:00",
            ],
            "open": [100.0, 101.0, 102.0],
            "high": [102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0],
            "close": [101.0, 102.0, 103.0],
        }
    )

    with pytest.raises(ValueError, match="timestamps inválidos"):
        validate_time_series(df)


def test_missing_column_is_rejected() -> None:
    df = valid_data().drop(columns="volume", errors="ignore").drop(columns="close")

    with pytest.raises(ValueError, match="Faltan columnas"):
        validate_time_series(df)


def test_input_dataframe_is_not_modified() -> None:
    df = valid_data()
    original = df.copy(deep=True)

    validate_time_series(df)

    pd.testing.assert_frame_equal(df, original)


def test_boolean_prices_are_rejected() -> None:
    df = valid_data().assign(close=[101.0, True, 103.0])

    with pytest.raises(ValueError, match="no booleanos"):
        validate_time_series(df)
