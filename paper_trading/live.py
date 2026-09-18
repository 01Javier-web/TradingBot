"""Ciclo acotado de mercado en tiempo real para paper trading."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from time import sleep
from typing import Callable, Protocol

import pandas as pd

from paper_trading.guards import assert_simulation_only
from paper_trading.session import PaperSessionResult, PaperTradingSession


class MarketFeed(Protocol):
    def latest(self, symbol: str, timeframe: int, count: int = 100) -> pd.DataFrame: ...


@dataclass(frozen=True)
class LivePaperRun:
    polls: int
    rows: int
    session: PaperSessionResult
    mode: str = "simulation-first"
    execution_authorized: bool = False


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
    """Lee un número finito de lotes y los procesa sin ejecución real."""
    assert_simulation_only(execution_authorized=False, component="run_bounded_paper_loop")

    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("symbol debe ser texto no vacío")
    for name, value in (("timeframe", timeframe), ("polls", polls), ("count", count)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} debe ser un entero mayor que 0")
    if isinstance(interval_seconds, bool) or not isinstance(interval_seconds, (int, float)) or not isfinite(float(interval_seconds)) or interval_seconds < 0:
        raise ValueError("interval_seconds debe ser finito y no negativo")

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
