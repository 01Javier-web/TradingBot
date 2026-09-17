"""Pruebas de métricas y observabilidad."""

from datetime import datetime

from analytics.events import summarize_events
from analytics.report import build_report
from backtesting.models import BacktestResult, PositionSide, Trade


def test_performance_report_aggregates_backtest_metrics() -> None:
    trades = (
        Trade(datetime(2026, 1, 1), datetime(2026, 1, 2), PositionSide.BUY, 100, 110, 1, 10, 1),
        Trade(datetime(2026, 1, 3), datetime(2026, 1, 4), PositionSide.SELL, 110, 105, 1, 5, 1),
    )
    result = BacktestResult(10_000, 10_013, trades, (10_000, 10_009, 10_013))
    report = build_report(result)
    assert report.trades == 2
    assert report.net_pnl == 13
    assert report.win_rate == 1.0
    assert report.profit_factor > 0


def test_event_summary_counts_actions() -> None:
    events = [{"action": "OPEN"}, {"action": "CLOSE"}, {"action": "CLOSE"}, {"action": "REJECTED"}]
    assert summarize_events(events) == {"OPEN": 1, "CLOSE": 2, "REJECTED": 1}
