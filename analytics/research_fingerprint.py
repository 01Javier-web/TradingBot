"""Huella reproducible de datos para investigaciones."""

from __future__ import annotations

from hashlib import sha256

import pandas as pd

from data.quality import validate_time_series


_REQUIRED_COLUMNS = ("time", "open", "high", "low", "close")


def _canonical_timestamp(value: object) -> str:
    """Normaliza timestamps a UTC ISO-8601 con representación estable."""
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        raise ValueError("time debe tener zona horaria")
    return timestamp.tz_convert("UTC").isoformat()


def fingerprint_dataframe(df: pd.DataFrame) -> str:
    """Genera una huella SHA-256 de datos de mercado estrictamente validados.

    La huella depende del orden temporal y de los cinco campos de mercado
    utilizados por el backtester. Columnas auxiliares no forman parte de la
    identidad porque son recalculadas por la estrategia.
    """
    validated = validate_time_series(df)
    frame = validated.loc[:, _REQUIRED_COLUMNS].copy()

    canonical_rows = [
        "|".join(
            [
                _canonical_timestamp(row.time),
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


__all__ = ["fingerprint_dataframe"]
