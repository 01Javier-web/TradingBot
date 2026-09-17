"""Runner simple para alimentar paper trading con un DataFrame."""

from __future__ import annotations

import pandas as pd

from paper_trading.engine import PaperTradingEngine


def run_dataframe(df: pd.DataFrame, engine: PaperTradingEngine) -> list[str]:
    """Procesa las velas en orden temporal y devuelve los eventos generados."""
    if "time" not in df.columns:
        raise ValueError("Falta la columna 'time'")
    if not df["time"].is_monotonic_increasing:
        raise ValueError("El DataFrame debe estar ordenado por tiempo")
    return [engine.process(row) for _, row in df.iterrows()]
