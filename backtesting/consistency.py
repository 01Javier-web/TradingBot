"""Comprobaciones de consistencia para resultados de backtesting."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from backtesting.models import BacktestResult, PositionSide


@dataclass(frozen=True)
class BacktestConsistency:
    """Estado de consistencia interna de un resultado de backtest."""

    valid: bool
    issues: tuple[str, ...]


def validate_backtest_result(result: BacktestResult) -> BacktestConsistency:
    """Comprueba balances, curva de equity y operaciones sin alterar el resultado."""
    if not isinstance(result, BacktestResult):
        raise ValueError("result debe ser BacktestResult")
    issues: list[str] = []

    if not isfinite(result.initial_balance) or result.initial_balance <= 0:
        issues.append("initial_balance debe ser finito y positivo.")
    if not isfinite(result.final_balance):
        issues.append("final_balance debe ser finito.")
    if not result.equity_curve:
        issues.append("La curva de equity no puede estar vacía.")
    else:
        if result.equity_curve[0] != result.initial_balance:
            issues.append("La curva de equity debe comenzar con initial_balance.")
        if result.equity_curve[-1] != result.final_balance:
            issues.append("La curva de equity debe terminar con final_balance.")

    for index, value in enumerate(result.equity_curve, start=1):
        if not isfinite(value):
            issues.append(f"Equity {index}: valor no finito.")

    calculated = result.initial_balance
    previous_exit = None
    for index, trade in enumerate(result.trades, start=1):
        if not isinstance(trade.side, PositionSide):
            issues.append(f"Trade {index}: side inválido.")
        if not all(
            isfinite(value)
            for value in (
                trade.entry_price,
                trade.exit_price,
                trade.quantity,
                trade.gross_pnl,
                trade.costs,
            )
        ):
            issues.append(f"Trade {index}: contiene valores no finitos.")
        if trade.entry_price <= 0 or trade.exit_price <= 0:
            issues.append(f"Trade {index}: los precios deben ser positivos.")
        if trade.quantity <= 0:
            issues.append(f"Trade {index}: quantity debe ser positiva.")
        if trade.costs < 0:
            issues.append(f"Trade {index}: costs no puede ser negativo.")
        try:
            if trade.entry_time >= trade.exit_time:
                issues.append(f"Trade {index}: exit_time debe ser posterior a entry_time.")
        except TypeError:
            issues.append(f"Trade {index}: timestamps no comparables.")
        if previous_exit is not None:
            try:
                if trade.entry_time < previous_exit:
                    issues.append(f"Trade {index}: se solapa temporalmente con la operación anterior.")
            except TypeError:
                issues.append(f"Trade {index}: timestamps no comparables.")
        previous_exit = trade.exit_time
        calculated += trade.net_pnl

    if isfinite(result.final_balance) and abs(calculated - result.final_balance) > 1e-8:
        issues.append("final_balance no coincide con la suma de los resultados de las operaciones.")

    return BacktestConsistency(valid=not issues, issues=tuple(issues))
