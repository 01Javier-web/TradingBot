"""Pruebas del procesamiento incremental de snapshots."""

import pandas as pd

from paper_trading.engine import PaperTradingEngine
from paper_trading.live import run_bounded_paper_stream_loop
from paper_trading.portfolio import PaperPortfolio
from paper_trading.stream import PaperTradingStream


def _data(start: int, rows: int, *, offset: int = 0) -> pd.DataFrame:
    close = pd.Series(range(start, start + rows), dtype=float)
    return pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=rows, freq="15min") + pd.Timedelta(minutes=15 * offset),
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
    assert result.last_time == pd.Timestamp(extended["time"].iloc[-1], tz="UTC")


def test_stream_generates_strategy_signals_before_processing() -> None:
    engine = PaperTradingEngine(PaperPortfolio())
    stream = PaperTradingStream(engine)
    result = stream.ingest(_data(100, 60))
    assert result.rows_processed == 60
    assert result.mode == "simulation-first"
    assert result.execution_authorized is False
    assert all(event["action"] in {"OPEN", "CLOSE", "STOP_LOSS", "REJECTED", "KILL_SWITCH"} for event in engine.history)


def test_stream_keeps_execution_disabled() -> None:
    stream = PaperTradingStream(PaperTradingEngine(PaperPortfolio()))
    result = stream.ingest(_data(100, 5))
    assert result.mode == "simulation-first"
    assert result.execution_authorized is False


class RollingFeed:
    def __init__(self) -> None:
        self.calls = 0

    def latest(self, symbol: str, timeframe: int, count: int = 100) -> pd.DataFrame:
        self.calls += 1
        assert symbol == "TEST"
        assert timeframe == 15
        return _data(100, count, offset=self.calls - 1)


def test_bounded_stream_loop_reuses_one_virtual_session_and_deduplicates() -> None:
    feed = RollingFeed()
    result = run_bounded_paper_stream_loop(
        feed,
        symbol="TEST",
        timeframe=15,
        polls=3,
        count=20,
    )
    assert feed.calls == 3
    assert result.polls == 3
    assert result.rows_received == 60
    assert result.rows_processed == 22
    assert result.last_time is not None
    assert result.mode == "simulation-first"
    assert result.execution_authorized is False
    assert result.portfolio.position is not None or result.portfolio.balance == result.portfolio.initial_balance


def test_stream_recalculates_indicators_with_prior_history(monkeypatch) -> None:
    calls = []

    def fake_signals(frame, config=None):
        calls.append(len(frame))
        result = frame.copy()
        result["signal"] = "WAIT"
        return result

    monkeypatch.setattr("paper_trading.stream.generate_signals", fake_signals)
    stream = PaperTradingStream(PaperTradingEngine(PaperPortfolio()))
    stream.ingest(_data(100, 20))
    stream.ingest(_data(120, 5, offset=20))

    assert calls == [20, 25]
