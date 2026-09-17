"""Prueba de extremo a extremo de una sesión de paper trading."""

import pandas as pd
import pytest

from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from strategy.signals import Signal


def test_complete_paper_session_matches_portfolio_and_report() -> None:
    portfolio = PaperPortfolio(10_000)
    engine = PaperTradingEngine(portfolio, quantity=2)

    assert engine.process(pd.Series({"close": 100.0, "atr": 5.0, "signal": Signal.BUY})) == "OPEN BUY"
    assert engine.process(pd.Series({"close": 110.0, "signal": Signal.SELL})) == "CLOSE BUY: pnl=20.000000"

    report = engine.performance_report()

    assert portfolio.balance == pytest.approx(10_020)
    assert report.initial_balance == pytest.approx(10_000)
    assert report.final_balance == pytest.approx(10_020)
    assert report.realized_pnl == pytest.approx(20)
    assert report.closed_trades == 1
    assert report.winning_trades == 1
    assert report.losing_trades == 0
    assert report.consistent is True
    assert report.open_position is False


def test_open_position_remains_unrealized_in_session_report() -> None:
    portfolio = PaperPortfolio(10_000)
    engine = PaperTradingEngine(portfolio, quantity=1)

    assert engine.process(pd.Series({"close": 100.0, "atr": 5.0, "signal": Signal.BUY})) == "OPEN BUY"
    report = engine.performance_report()

    assert report.final_balance == pytest.approx(10_000)
    assert report.realized_pnl == pytest.approx(0)
    assert report.closed_trades == 0
    assert report.open_position is True
    assert report.consistent is True
