"""Formato textual estable para resultados de backtesting."""

from __future__ import annotations

from backtesting.consistency import validate_backtest_result
from backtesting.metrics import max_drawdown, profit_factor, win_rate
from backtesting.models import BacktestResult


def format_backtest_result(result: BacktestResult) -> str:
    """Genera un resumen humano sin ordenar ni seleccionar estrategias."""
    consistency = validate_backtest_result(result)
    pnls = [trade.net_pnl for trade in result.trades]
    lines = [
        "=== TradingBot Backtest Report ===",
        f"Balance inicial: {result.initial_balance}",
        f"Balance final: {result.final_balance}",
        f"PnL neto: {result.net_pnl}",
        f"Operaciones: {len(result.trades)}",
        f"Win rate: {win_rate(pnls):.1%}",
        f"Profit factor: {profit_factor(pnls)}",
        f"Max drawdown: {max_drawdown(result.equity_curve):.1%}",
        f"Consistencia: {'OK' if consistency.valid else 'ERROR'}",
    ]
    if consistency.issues:
        lines.append("Problemas:")
        lines.extend(f"- {issue}" for issue in consistency.issues)
    lines.append("Modo: simulation-first")
    return "\n".join(lines)
