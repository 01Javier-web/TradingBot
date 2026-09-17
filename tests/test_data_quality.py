"""Pruebas de integridad de datos de mercado."""

import pandas as pd
import pytest

from data.quality import validate_time_series


def valid_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=3, freq="15min", tz="UTC"),
            "open": [100, 101, 102],
            "high": [102, 103, 104],
            "low": [99, 100, 101],
            "close": [101, 102, 103],
        }
    )


def test_valid_time_series_is_accepted() -> None:
    result = validate_time_series(valid_data())
    assert len(result) == 3
    assert str(result["time"].dt.tz) == "UTC"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda df: df.iloc[::-1],
        lambda df: pd.concat([df, df.iloc[[0]]], ignore_index=True),
        lambda df: df.assign(high=[98, 103, 104]),
        lambda df: df.assign(close=[100, 0, 103]),
    ],
)
def test_invalid_time_series_is_rejected(mutate) -> None:
    with pytest.raises(ValueError):
        validate_time_series(mutate(valid_data()))
