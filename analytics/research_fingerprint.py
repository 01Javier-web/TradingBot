"""Huella reproducible de datos para investigaciones."""

from __future__ import annotations

from hashlib import sha256

import pandas as pd


_REQUIRED_COLUMNS = ("time", "open", "high", "low", "close")


def fingerprint_dataframe(df: pd.DataFrame) -> str:
    """Genera una huella SHA-256 determinista de los datos OHLC usados."""
    missing = [column for column in _REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(missing)}")

    frame = df.loc[:, _REQUIRED_COLUMNS].copy()
    frame["time"] = pd.to_datetime(frame["time"], utc=True).astype("string")
    for column in _REQUIRED_COLUMNS[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")

    canonical = frame.to_csv(
        index=False,
        lineterminator="\n",
        float_format=".17g",
    )
    return sha256(canonical.encode("utf-8")).hexdigest()
