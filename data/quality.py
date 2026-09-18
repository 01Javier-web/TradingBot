"""Validaciones de calidad para series temporales de mercado."""

from __future__ import annotations

from math import isfinite

import pandas as pd


REQUIRED_OHLC = ("time", "open", "high", "low", "close")


def validate_time_series(df: pd.DataFrame) -> pd.DataFrame:
    """Valida integridad temporal y OHLC sin modificar el DataFrame original."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df debe ser un pandas.DataFrame")

    missing = [column for column in REQUIRED_OHLC if column not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas: {', '.join(missing)}")

    result = df.copy()
    result["time"] = pd.to_datetime(result["time"], errors="coerce", utc=True)
    if result["time"].isna().any():
        raise ValueError("Existen timestamps inválidos")
    if result["time"].duplicated().any():
        raise ValueError("Existen timestamps duplicados")
    if not result["time"].is_monotonic_increasing:
        raise ValueError("Los timestamps deben estar ordenados de forma estrictamente creciente")

    price_columns = list(REQUIRED_OHLC[1:])
    for column in price_columns:
        if result[column].map(lambda value: isinstance(value, bool)).any():
            raise ValueError("Los precios deben ser numéricos, no booleanos")
        result[column] = pd.to_numeric(result[column], errors="coerce")

    if result[price_columns].isna().any().any():
        raise ValueError("Existen precios inválidos o ausentes")
    if not result[price_columns].map(lambda value: isfinite(float(value))).all().all():
        raise ValueError("Existen precios infinitos o no finitos")
    if (result[price_columns] <= 0).any().any():
        raise ValueError("Los precios deben ser mayores que 0")

    if (result["high"] < result[price_columns].drop(columns=["high"]).max(axis=1)).any():
        raise ValueError("high no puede ser menor que open, close o low")
    if (result["low"] > result[price_columns].drop(columns=["low"]).min(axis=1)).any():
        raise ValueError("low no puede ser mayor que open, close o high")

    return result


__all__ = ["REQUIRED_OHLC", "validate_time_series"]
