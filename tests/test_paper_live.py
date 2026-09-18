"""Pruebas del ciclo acotado de paper trading."""

import pandas as pd
import pytest

from paper_trading.live import run_bounded_paper_loop
from paper_trading.portfolio import PaperPortfolio
from paper_trading.session import PaperTradingSession


def _data(rows: int = 25) -> pd.DataFrame:
    close = pd.Series(range(10, 10 + rows), dtype=float)
    return pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=rows, freq="15min"),
        "open": close,
        "high": close + 1,
        "low": close - 1,
        "close": close,
    })


class FakeFeed:
    def __init__(self) -> None:
        self.calls = 0

    def latest(self, symbol: str, timeframe: int, count: int = 100) -> pd.DataFrame:
        self.calls += 1
        assert symbol == "TEST"
        assert timeframe == 15
        assert count == 25
        return _data(count)


def test_bounded_loop_is_finite_and_paper_only() -> None:
    feed = FakeFeed()
    result = run_bounded_paper_loop(
        feed,
        lambda: PaperTradingSession(PaperPortfolio()),
        symbol="TEST",
        timeframe=15,
        polls=3,
        count=25,
    )
    assert feed.calls == 3
    assert result.polls == 3
    assert result.rows == 75
    assert result.mode == "simulation-first"
    assert result.execution_authorized is False
    assert result.session.audit.valid


def test_loop_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        run_bounded_paper_loop(
            FakeFeed(),
            lambda: PaperTradingSession(PaperPortfolio()),
            symbol="TEST",
            timeframe=15,
            polls=0,
        )


def test_loop_rejects_non_session_factory_result() -> None:
    with pytest.raises(TypeError, match="PaperTradingSession"):
        run_bounded_paper_loop(
            FakeFeed(),
            lambda: object(),
            symbol="TEST",
            timeframe=15,
            count=25,
        )
