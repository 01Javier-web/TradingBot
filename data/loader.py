"""Carga y normaliza datos históricos para el TradingBot."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from data.quality import validate_time_series

PathLike = Union[str, Path]


def load_csv(path: PathLike) -> pd.DataFrame:
    """Carga un CSV de velas y devuelve un DataFrame validado."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"No existe el archivo de datos: {file_path}")

    df = pd.read_csv(file_path)
    return validate_market_data(df)


def validate_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """Valida OHLC y tiempo sin ordenar ni eliminar datos silenciosamente."""
    return validate_time_series(df)


__all__ = ["load_csv", "validate_market_data"]
