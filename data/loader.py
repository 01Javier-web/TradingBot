"""Carga y normaliza datos históricos para el TradingBot."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

PathLike = Union[str, Path]

REQUIRED_COLUMNS = ("time", "open", "high", "low", "close")


def load_csv(path: PathLike) -> pd.DataFrame:
    """Carga un CSV de velas y devuelve un DataFrame validado."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"No existe el archivo de datos: {file_path}")

    df = pd.read_csv(file_path)
    return validate_market_data(df)


def validate_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """Valida columnas básicas y normaliza tiempo y orden de las velas."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(missing)}")

    result = df.copy()
    result["time"] = pd.to_datetime(result["time"], errors="coerce")

    if result["time"].isna().any():
        raise ValueError("La columna 'time' contiene fechas inválidas")

    for column in ("open", "high", "low", "close"):
        result[column] = pd.to_numeric(result[column], errors="coerce")

    if result[["open", "high", "low", "close"]].isna().any().any():
        raise ValueError("Los precios contienen valores no numéricos o vacíos")

    if (result["high"] < result["low"]).any():
        raise ValueError("Se encontraron velas con high menor que low")

    return result.sort_values("time").drop_duplicates("time").reset_index(drop=True)
