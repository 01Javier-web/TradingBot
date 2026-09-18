"""Procesador incremental de snapshots para paper trading."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data.quality import validate_time_series
from paper_trading.engine import PaperTradingEngine


@dataclass(frozen=True)
class StreamBatch:
    rows_received: int
    rows_processed: int
    events_created: int
    last_time: pd.Timestamp | None
    mode: str = "simulation-first"
    execution_authorized: bool = False


class PaperTradingStream:
    """Consume snapshots repetidos sin reprocesar velas ya vistas."""

    def __init__(self, engine: PaperTradingEngine) -> None:
        self.engine = engine
        self._last_time: pd.Timestamp | None = None
        self._processed_rows = 0

    @property
    def last_time(self) -> pd.Timestamp | None:
        return self._last_time

    def ingest(self, df: pd.DataFrame) -> StreamBatch:
        """Valida un snapshot y procesa únicamente velas nuevas."""
        data = validate_time_series(df)
        if self._last_time is not None:
            data = data[data["time"] > self._last_time].copy()

        before = len(self.engine.history)
        for _, row in data.iterrows():
            self.engine.process(row)

        if not data.empty:
            self._last_time = data["time"].iloc[-1]
        self._processed_rows += len(data)

        return StreamBatch(
            rows_received=len(df),
            rows_processed=len(data),
            events_created=len(self.engine.history) - before,
            last_time=self._last_time,
        )


__all__ = ["PaperTradingStream", "StreamBatch"]
