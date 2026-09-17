"""Pruebas del reporte de rendimiento de paper trading."""

import pytest

from analytics.paper_report import build_paper_report
from backtesting.models import PositionSide
from paper_trading.portfolio import PaperPortfolio


def test_report_matches_realized_pnl_and_balance() -> None:
    portfolio = PaperPortfolio(10_000)
    portfolio.open_position(PositionSide.BUY, 100, 2, 95)
    portfolio.close_position(110)

    report = build_paper_report(
        portfolio,
        [{"action": "OPEN"}, {"action": "CLOSE", "pnl": 20.0}],
        initial_balance=10_000,
    )

    assert report.final_balance == pytest.approx(10_020)
    assert report.realized_pnl == pytest.approx(20)
    assert report.closed_trades == 1
    assert report.winning_trades == 1
    assert report.losing_trades == 0
    assert report.win_rate == pytest.approx(1.0)
    assert report.profit_factor == float("inf")
    assert report.consistent is True
    assert report.open_position is False


def test_report_includes_stop_losses_as_closed_trades() -> None:
    portfolio = PaperPortfolio(10_000)
    portfolio.open_position(PositionSide.BUY, 100, 1, 95)
    portfolio.close_position(95)

    report = build_paper_report(
        portfolio,
        [{"action": "STOP_LOSS", "pnl": -5.0}],
        initial_balance=10_000,
    )

    assert report.realized_pnl == pytest.approx(-5)
    assert report.closed_trades == 1
    assert report.losing_trades == 1
    assert report.win_rate == 0.0
    assert report.profit_factor == 0.0
    assert report.consistent is True


def test_open_position_is_not_counted_as_realized_trade() -> None:
    portfolio = PaperPortfolio(10_000)
    portfolio.open_position(PositionSide.BUY, 100, 1, 95)

    report = build_paper_report(
        portfolio,
        [{"action": "OPEN", "price": 100.0}],
        initial_balance=10_000,
    )

    assert report.closed_trades == 0
    assert report.realized_pnl == 0.0
    assert report.final_balance == 10_000
    assert report.open_position is True
    assert report.consistent is True


def test_report_detects_balance_inconsistency() -> None:
    portfolio = PaperPortfolio(10_000)
    report = build_paper_report(
        portfolio,
        [{"action": "CLOSE", "pnl": 25.0}],
        initial_balance=10_000,
    )

    assert report.consistent is False
    assert report.consistency_issue is not None
