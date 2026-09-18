"""Partición temporal para validación fuera de muestra."""

from __future__ import annotations

import pandas as pd

from data.quality import validate_time_series


def chronological_split(
    df: pd.DataFrame,
    train_ratio: float = 0.7,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Divide datos validados sin mezclar el futuro con el pasado."""
    if isinstance(train_ratio, bool) or not isinstance(train_ratio, (int, float)):
        raise ValueError("train_ratio debe ser numérico")
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio debe estar entre 0 y 1")
    data = validate_time_series(df)
    if len(data) < 2:
        raise ValueError("Se requieren al menos 2 filas")

    cut = int(len(data) * train_ratio)
    cut = max(1, min(cut, len(data) - 1))
    train = data.iloc[:cut].copy()
    test = data.iloc[cut:].copy()
    if train.iloc[-1]["time"] >= test.iloc[0]["time"]:
        raise ValueError("La partición train/test debe ser estrictamente temporal")
    return train, test


__all__ = ["chronological_split"]
