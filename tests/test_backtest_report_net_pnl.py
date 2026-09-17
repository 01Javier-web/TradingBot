"""Verifica que las métricas del reporte usan PnL neto."""

from backtesting.models import BacktestResult, PositionSide, Trade
from analytics.backtest_report import backtest_to_dict


def test_backtest_report_metrics_use_net_pnl() -> None:
    trade = Trade(1, 2, PositionSide.BUY, 10.0, 12.0, 1.0, 2.0, 0.5)
    result = BacktestResult(100.0, 101.5, (trade,), (100.0, 101.5))

    report = backtest_to_dict(result)

    assert report["win_rate"] == 1.0
    assert report["profit_factor"] == float("inf")
