"""Validaciones de calidad para series temporales de mercado."""

from __future__ import annotations

import pandas as pd


REQUIRED_OHLC = ("time", "open", "high", "low", "close")


def validate_time_series(df: pd.DataFrame) -> pd.DataFrame:
    """Valida integridad temporal y OHLC sin modificar el DataFrame original."""
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
        raise ValueError("Los timestamps deben estar ordenados")

    for column in REQUIRED_OHLC[1:]:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    if result[list(REQUIRED_OHLC[1:])].isna().any().any():
        raise ValueError("Existen precios inválidos")
    if (result["high"] < result[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("high no puede ser menor que open, close o low")
    if (result["low"] > result[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("low no puede ser mayor que open, close o high")
    if (result[list(REQUIRED_OHLC[1:])] <= 0).any().any():
        raise ValueError("Los precios deben ser mayores que 0")

    return result
