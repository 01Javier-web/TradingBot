"""Pruebas de consistencia interna de resultados de backtesting."""

from backtesting.consistency import validate_backtest_result
from backtesting.models import BacktestResult, PositionSide, Trade


def _valid_result() -> BacktestResult:
    trade = Trade(1, 2, PositionSide.BUY, 10.0, 12.0, 1.0, 2.0, 0.5)
    return BacktestResult(100.0, 101.5, (trade,), (100.0, 101.5))


def _invalid_result(
    initial_balance: float,
    final_balance: float,
    trades: tuple,
    equity_curve: tuple,
) -> BacktestResult:
    result = object.__new__(BacktestResult)
    object.__setattr__(result, "initial_balance", initial_balance)
    object.__setattr__(result, "final_balance", final_balance)
    object.__setattr__(result, "trades", trades)
    object.__setattr__(result, "equity_curve", equity_curve)
    return result


def _invalid_trade(quantity: float) -> Trade:
    trade = object.__new__(Trade)
    object.__setattr__(trade, "entry_time", 1)
    object.__setattr__(trade, "exit_time", 2)
    object.__setattr__(trade, "side", PositionSide.BUY)
    object.__setattr__(trade, "entry_price", 10.0)
    object.__setattr__(trade, "exit_price", 12.0)
    object.__setattr__(trade, "quantity", quantity)
    object.__setattr__(trade, "gross_pnl", 2.0)
    object.__setattr__(trade, "costs", 0.5)
    return trade


def test_valid_backtest_result_is_accepted() -> None:
    result = validate_backtest_result(_valid_result())

    assert result.valid is True
    assert result.issues == ()


def test_equity_must_start_at_initial_balance() -> None:
    result = _valid_result()
    invalid = _invalid_result(result.initial_balance, result.final_balance, result.trades, (99.0, 101.5))

    check = validate_backtest_result(invalid)

    assert check.valid is False
    assert any("comenzar" in issue for issue in check.issues)


def test_final_balance_must_match_trade_results() -> None:
    result = _valid_result()
    invalid = _invalid_result(result.initial_balance, 999.0, result.trades, result.equity_curve)

    check = validate_backtest_result(invalid)

    assert check.valid is False
    assert any("no coincide" in issue for issue in check.issues)


def test_invalid_trade_values_are_rejected() -> None:
    trade = _invalid_trade(0.0)
    result = _invalid_result(100.0, 101.5, (trade,), (100.0, 101.5))

    check = validate_backtest_result(result)

    assert check.valid is False
    assert any("quantity" in issue for issue in check.issues)
