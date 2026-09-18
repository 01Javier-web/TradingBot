"""Ciclos acotados de mercado en tiempo real para paper trading."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from time import sleep
from typing import Callable, Protocol

import pandas as pd

from paper_trading.engine import PaperTradingEngine
from paper_trading.guards import assert_simulation_only
from paper_trading.portfolio import PaperPortfolio
from paper_trading.session import PaperSessionResult, PaperTradingSession
from paper_trading.stream import PaperTradingStream
from strategy.signals import StrategyConfig


class MarketFeed(Protocol):
    def latest(self, symbol: str, timeframe: int, count: int = 100) -> pd.DataFrame: ...


@dataclass(frozen=True)
class LivePaperRun:
    polls: int
    rows: int
    session: PaperSessionResult
    mode: str = "simulation-first"
    execution_authorized: bool = False


@dataclass(frozen=True)
class LivePaperStreamRun:
    """Resultado de varios snapshots procesados sobre un único portafolio virtual."""
    polls: int
    rows_received: int
    rows_processed: int
    events_created: int
    last_time: pd.Timestamp | None
    portfolio: PaperPortfolio
    engine: PaperTradingEngine
    mode: str = "simulation-first"
    execution_authorized: bool = False


def _validate_loop_config(symbol: str, timeframe: int, polls: int, count: int, interval_seconds: float) -> None:
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("symbol debe ser texto no vacío")
    for name, value in (("timeframe", timeframe), ("polls", polls), ("count", count)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} debe ser un entero mayor que 0")
    if (isinstance(interval_seconds, bool) or not isinstance(interval_seconds, (int, float))
            or not isfinite(float(interval_seconds)) or interval_seconds < 0):
        raise ValueError("interval_seconds debe ser finito y no negativo")


def run_bounded_paper_loop(
    feed: MarketFeed,
    session_factory: Callable[[], PaperTradingSession],
    *,
    symbol: str,
    timeframe: int,
    polls: int = 1,
    count: int = 100,
    interval_seconds: float = 0.0,
) -> LivePaperRun:
    """Lee lotes independientes y los procesa sin ejecución real."""
    assert_simulation_only(execution_authorized=False, component="run_bounded_paper_loop")
    _validate_loop_config(symbol, timeframe, polls, count, interval_seconds)
    last_result: PaperSessionResult | None = None
    total_rows = 0
    for index in range(polls):
        data = feed.latest(symbol, timeframe, count)
        if not isinstance(data, pd.DataFrame):
            raise TypeError("feed.latest debe devolver un DataFrame")
        session = session_factory()
        if not isinstance(session, PaperTradingSession):
            raise TypeError("session_factory debe devolver PaperTradingSession")
        last_result = session.run(data)
        total_rows += len(data)
        if index + 1 < polls and interval_seconds:
            sleep(interval_seconds)
    assert last_result is not None
    return LivePaperRun(polls=polls, rows=total_rows, session=last_result)


def run_bounded_paper_stream_loop(
    feed: MarketFeed,
    *,
    symbol: str,
    timeframe: int,
    polls: int = 1,
    count: int = 100,
    interval_seconds: float = 0.0,
    portfolio: PaperPortfolio | None = None,
    config: StrategyConfig | None = None,
) -> LivePaperStreamRun:
    """Procesa snapshots consecutivos sobre una única sesión virtual incremental."""
    assert_simulation_only(execution_authorized=False, component="run_bounded_paper_stream_loop")
    _validate_loop_config(symbol, timeframe, polls, count, interval_seconds)
    virtual_portfolio = portfolio or PaperPortfolio()
    engine = PaperTradingEngine(virtual_portfolio)
    stream = PaperTradingStream(engine, config=config)
    rows_received = 0
    rows_processed = 0
    events_created = 0
    for index in range(polls):
        data = feed.latest(symbol, timeframe, count)
        if not isinstance(data, pd.DataFrame):
            raise TypeError("feed.latest debe devolver un DataFrame")
        batch = stream.ingest(data)
        rows_received += batch.rows_received
        rows_processed += batch.rows_processed
        events_created += batch.events_created
        if index + 1 < polls and interval_seconds:
            sleep(interval_seconds)
    return LivePaperStreamRun(
        polls=polls, rows_received=rows_received, rows_processed=rows_processed,
        events_created=events_created, last_time=stream.last_time,
        portfolio=virtual_portfolio, engine=engine,
    )


__all__ = [
    "LivePaperRun", "LivePaperStreamRun", "MarketFeed",
    "run_bounded_paper_loop", "run_bounded_paper_stream_loop",
]
