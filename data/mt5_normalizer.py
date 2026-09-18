"""Normalización segura de datos de velas provenientes de MT5.

Este módulo solo transforma datos de lectura a DataFrame; no tiene acceso a
ningún método de ejecución de órdenes.
"""

from __future__ import annotations

from collections.abc import Iterable
from math import isfinite

import pandas as pd

from data.quality import validate_time_series


REQUIRED_COLUMNS = ("time", "open", "high", "low", "close")


def normalize_market_rates(rates: object) -> pd.DataFrame:
    """Convierte rates de MT5 a OHLC validado y ordenado cronológicamente.

    Acepta el ndarray estructurado que devuelve MT5 y también iterables de
    registros/diccionarios con las cinco columnas requeridas.
    """
    if rates is None:
        raise ValueError("rates no puede ser None")

    if isinstance(rates, pd.DataFrame):
        data = rates.copy()
    else:
        try:
            data = pd.DataFrame(rates)
        except (TypeError, ValueError) as exc:
            raise ValueError("rates no contiene datos tabulares válidos") from exc

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Faltan columnas de mercado: {', '.join(missing)}")

    data = data.loc[:, list(REQUIRED_COLUMNS)].copy()

    # MT5 normalmente entrega 'time' como epoch seconds. Si ya es datetime,
    # pandas lo conserva correctamente con utc=True.
    if pd.api.types.is_numeric_dtype(data["time"]):
        numeric_time = pd.to_numeric(data["time"], errors="coerce")
        if numeric_time.isna().any() or not numeric_time.map(lambda x: isfinite(float(x))).all():
            raise ValueError("Existen timestamps inválidos")
        data["time"] = pd.to_datetime(numeric_time, unit="s", utc=True, errors="coerce")
    else:
        data["time"] = pd.to_datetime(data["time"], utc=True, errors="coerce")

    return validate_time_series(data)


__all__ = ["REQUIRED_COLUMNS", "normalize_market_rates"]
