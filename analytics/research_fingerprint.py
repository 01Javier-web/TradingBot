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

    canonical_rows = [
        "|".join(
            [
                str(row.time),
                format(row.open, ".17g"),
                format(row.high, ".17g"),
                format(row.low, ".17g"),
                format(row.close, ".17g"),
            ]
        )
        for row in frame.itertuples(index=False)
    ]
    canonical = "\n".join(canonical_rows) + "\n"
    return sha256(canonical.encode("utf-8")).hexdigest()
