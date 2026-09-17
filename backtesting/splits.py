"""Partición temporal para validación fuera de muestra."""

from __future__ import annotations

import pandas as pd


def chronological_split(df: pd.DataFrame, train_ratio: float = 0.7) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Divide datos sin mezclar el futuro con el pasado."""
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio debe estar entre 0 y 1")
    if len(df) < 2:
        raise ValueError("Se requieren al menos 2 filas")
    if "time" not in df.columns or not df["time"].is_monotonic_increasing:
        raise ValueError("Los datos deben tener timestamps ordenados")

    cut = int(len(df) * train_ratio)
    cut = max(1, min(cut, len(df) - 1))
    return df.iloc[:cut].copy(), df.iloc[cut:].copy()
