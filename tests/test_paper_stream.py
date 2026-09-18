"""Pruebas del procesamiento incremental de snapshots."""

import pandas as pd

from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from paper_trading.stream import PaperTradingStream


def _data(start: int, rows: int) -> pd.DataFrame:
    close = pd.Series(range(start, start + rows), dtype=float)
    return pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=rows, freq="15min"),
        "open": close,
        "high": close + 1,
        "low": (close - 1).clip(lower=0.1),
        "close": close,
    })


def test_stream_does_not_reprocess_identical_snapshot() -> None:
    stream = PaperTradingStream(PaperTradingEngine(PaperPortfolio()))

    first = stream.ingest(_data(100, 20))
    second = stream.ingest(_data(100, 20))

    assert first.rows_received == 20
    assert first.rows_processed == 20
    assert second.rows_received == 20
    assert second.rows_processed == 0
    assert second.events_created == 0


def test_stream_processes_only_new_tail() -> None:
    stream = PaperTradingStream(PaperTradingEngine(PaperPortfolio()))

    stream.ingest(_data(100, 20))
    extended = _data(100, 25)
    result = stream.ingest(extended)

    assert result.rows_received == 25
    assert result.rows_processed == 5
    assert result.last_time == extended["time"].iloc[-1]


def test_stream_keeps_execution_disabled() -> None:
    stream = PaperTradingStream(PaperTradingEngine(PaperPortfolio()))

    result = stream.ingest(_data(100, 5))

    assert result.mode == "simulation-first"
    assert result.execution_authorized is False
