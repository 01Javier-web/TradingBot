"""Procesador incremental de snapshots para paper trading."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data.quality import validate_time_series
from paper_trading.engine import PaperTradingEngine
from strategy.signals import StrategyConfig, generate_signals


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

    def __init__(
        self,
        engine: PaperTradingEngine,
        config: StrategyConfig | None = None,
    ) -> None:
        self.engine = engine
        self.config = config or StrategyConfig()
        self._last_time: pd.Timestamp | None = None
        self._processed_rows = 0
        self._market_history = pd.DataFrame()

    @property
    def last_time(self) -> pd.Timestamp | None:
        return self._last_time

    @property
    def processed_rows(self) -> int:
        return self._processed_rows

    def ingest(self, df: pd.DataFrame) -> StreamBatch:
        """Valida un snapshot, calcula señales y procesa únicamente velas nuevas."""
        snapshot = validate_time_series(df)
        if self._last_time is not None:
            data = snapshot[snapshot["time"] > self._last_time].copy()
        else:
            data = snapshot.copy()

        before = len(self.engine.history)
        if not data.empty:
            # Los indicadores deben calcularse sobre el historial completo.
            # Calcularlos solo sobre el nuevo tail reinicia EMA/RSI/ATR y
            # puede producir señales diferentes a una sesión continua.
            self._market_history = pd.concat(
                [self._market_history, data],
                ignore_index=True,
            )
            self._market_history = validate_time_series(self._market_history)
            enriched = generate_signals(self._market_history, self.config)
            new_rows = enriched.tail(len(data))
            for _, row in new_rows.iterrows():
                self.engine.process(row)
            self._last_time = data["time"].iloc[-1]
            processed = len(data)
        else:
            processed = 0

        self._processed_rows += processed

        return StreamBatch(
            rows_received=len(df),
            rows_processed=processed,
            events_created=len(self.engine.history) - before,
            last_time=self._last_time,
        )


__all__ = ["PaperTradingStream", "StreamBatch"]
