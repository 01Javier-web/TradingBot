"""Pruebas del formato textual de backtesting."""

from backtesting.models import BacktestResult, PositionSide, Trade
from analytics.backtest_text import format_backtest_result


def _result() -> BacktestResult:
    trade = Trade(1, 2, PositionSide.BUY, 10.0, 12.0, 1.0, 2.0, 0.5)
    return BacktestResult(100.0, 101.5, (trade,), (100.0, 101.5))


def test_format_backtest_result_contains_core_sections() -> None:
    report = format_backtest_result(_result())

    assert "=== TradingBot Backtest Report ===" in report
    assert "Balance inicial: 100.0" in report
    assert "Balance final: 101.5" in report
    assert "PnL neto: 1.5" in report
    assert "Operaciones: 1" in report
    assert "Win rate: 100.0%" in report
    assert "Consistencia: OK" in report
    assert "Modo: simulation-first" in report


def test_format_backtest_result_reports_consistency_issues() -> None:
    result = _result()
    invalid = BacktestResult(result.initial_balance, 999.0, result.trades, result.equity_curve)

    report = format_backtest_result(invalid)

    assert "Consistencia: ERROR" in report
    assert "Problemas:" in report
    assert "no coincide" in report
