"""Pruebas de la huella reproducible de datos."""

import pandas as pd
import pytest

from analytics.research_fingerprint import fingerprint_dataframe


def _data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=3, freq="15min"),
            "open": [1.0, 2.0, 3.0],
            "high": [2.0, 3.0, 4.0],
            "low": [0.5, 1.5, 2.5],
            "close": [1.5, 2.5, 3.5],
        }
    )


def test_same_data_produces_same_fingerprint() -> None:
    assert fingerprint_dataframe(_data()) == fingerprint_dataframe(_data())


def test_data_change_produces_different_fingerprint() -> None:
    original = _data()
    changed = _data()
    changed.loc[1, "open"] = 2.25

    assert fingerprint_dataframe(original) != fingerprint_dataframe(changed)


def test_non_chronological_row_order_is_rejected() -> None:
    reordered = _data().iloc[::-1].reset_index(drop=True)

    with pytest.raises(ValueError, match="estrictamente creciente"):
        fingerprint_dataframe(reordered)


def test_missing_required_column_is_rejected() -> None:
    data = _data().drop(columns="close")

    with pytest.raises(ValueError, match="close"):
        fingerprint_dataframe(data)


def test_fingerprint_is_sha256_hex() -> None:
    fingerprint = fingerprint_dataframe(_data())

    assert len(fingerprint) == 64
    assert all(character in "0123456789abcdef" for character in fingerprint)
