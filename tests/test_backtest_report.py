"""Pruebas del reporte auditable de backtesting."""

from backtesting.models import BacktestResult, PositionSide, Trade
from analytics.backtest_report import backtest_to_dict


def _result() -> BacktestResult:
    trade = Trade(1, 2, PositionSide.BUY, 10.0, 12.0, 1.0, 2.0, 0.5)
    return BacktestResult(100.0, 101.5, (trade,), (100.0, 101.5))


def _invalid_result() -> BacktestResult:
    result = _result()
    invalid = object.__new__(BacktestResult)
    object.__setattr__(invalid, "initial_balance", result.initial_balance)
    object.__setattr__(invalid, "final_balance", 999.0)
    object.__setattr__(invalid, "trades", result.trades)
    object.__setattr__(invalid, "equity_curve", result.equity_curve)
    return invalid


def test_backtest_report_contains_core_metrics() -> None:
    report = backtest_to_dict(_result())

    assert report["initial_balance"] == 100.0
    assert report["final_balance"] == 101.5
    assert report["net_pnl"] == 1.5
    assert report["trades"] == 1
    assert report["win_rate"] == 1.0
    assert report["profit_factor"] == float("inf")
    assert report["max_drawdown"] == 0.0


def test_backtest_report_exposes_consistency_status() -> None:
    report = backtest_to_dict(_result())

    assert report["consistency"]["valid"] is True
    assert report["consistency"]["issues"] == []


def test_backtest_report_preserves_consistency_issues() -> None:
    report = backtest_to_dict(_invalid_result())

    assert report["consistency"]["valid"] is False
    assert any("no coincide" in issue for issue in report["consistency"]["issues"])
