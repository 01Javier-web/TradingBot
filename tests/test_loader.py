"""Pruebas de validación y normalización de datos de mercado."""

from pathlib import Path

import pandas as pd
import pytest

from data.loader import load_csv, validate_market_data


def _valid_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": ["2026-01-02 10:00", "2026-01-02 09:00"],
            "open": [101, 99],
            "high": [103, 101],
            "low": [100, 98],
            "close": [102, 100],
        }
    )


def test_validate_market_data_sorts_and_removes_duplicate_times() -> None:
    df = pd.concat([_valid_frame(), _valid_frame().iloc[[0]]], ignore_index=True)

    result = validate_market_data(df)

    assert result["time"].is_monotonic_increasing
    assert result["time"].is_unique
    assert len(result) == 2


def test_validate_market_data_requires_ohlc_columns() -> None:
    df = _valid_frame().drop(columns=["close"])

    with pytest.raises(ValueError, match="Faltan columnas requeridas"):
        validate_market_data(df)


def test_validate_market_data_rejects_invalid_time() -> None:
    df = _valid_frame()
    df.loc[0, "time"] = "fecha-invalida"

    with pytest.raises(ValueError, match="fechas inválidas"):
        validate_market_data(df)


def test_validate_market_data_rejects_non_numeric_prices() -> None:
    df = _valid_frame()
    df.loc[0, "close"] = "no-es-un-precio"

    with pytest.raises(ValueError, match="precios contienen"):
        validate_market_data(df)


def test_validate_market_data_rejects_inverted_range() -> None:
    df = _valid_frame()
    df.loc[0, "high"] = 95
    df.loc[0, "low"] = 100

    with pytest.raises(ValueError, match="high menor que low"):
        validate_market_data(df)


def test_load_csv_validates_file(tmp_path: Path) -> None:
    path = tmp_path / "candles.csv"
    _valid_frame().to_csv(path, index=False)

    result = load_csv(path)

    assert len(result) == 2
    assert list(result.columns) == ["time", "open", "high", "low", "close"]


def test_load_csv_raises_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No existe el archivo"):
        load_csv(tmp_path / "missing.csv")
