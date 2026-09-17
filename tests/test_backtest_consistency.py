"""Pruebas de consistencia interna de resultados de backtesting."""

from backtesting.consistency import validate_backtest_result
from backtesting.models import BacktestResult, PositionSide, Trade


def _valid_result() -> BacktestResult:
    trade = Trade(1, 2, PositionSide.BUY, 10.0, 12.0, 1.0, 2.0, 0.5)
    return BacktestResult(100.0, 101.5, (trade,), (100.0, 101.5))


def test_valid_backtest_result_is_accepted() -> None:
    result = validate_backtest_result(_valid_result())

    assert result.valid is True
    assert result.issues == ()


def test_equity_must_start_at_initial_balance() -> None:
    result = _valid_result()
    invalid = BacktestResult(result.initial_balance, result.final_balance, result.trades, (99.0, 101.5))

    check = validate_backtest_result(invalid)

    assert check.valid is False
    assert any("comenzar" in issue for issue in check.issues)


def test_final_balance_must_match_trade_results() -> None:
    result = _valid_result()
    invalid = BacktestResult(result.initial_balance, 999.0, result.trades, result.equity_curve)

    check = validate_backtest_result(invalid)

    assert check.valid is False
    assert any("no coincide" in issue for issue in check.issues)


def test_invalid_trade_values_are_rejected() -> None:
    trade = Trade(1, 2, PositionSide.BUY, 10.0, 12.0, 0.0, 2.0, 0.5)
    result = BacktestResult(100.0, 101.5, (trade,), (100.0, 101.5))

    check = validate_backtest_result(result)

    assert check.valid is False
    assert any("quantity" in issue for issue in check.issues)
