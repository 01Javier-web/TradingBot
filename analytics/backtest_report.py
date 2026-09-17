"""Reporte auditable para resultados de backtesting."""

from __future__ import annotations

from typing import Any

from backtesting.consistency import validate_backtest_result
from backtesting.metrics import max_drawdown, profit_factor, win_rate
from backtesting.models import BacktestResult


def backtest_to_dict(result: BacktestResult) -> dict[str, Any]:
    """Serializa métricas y consistencia sin seleccionar una estrategia."""
    consistency = validate_backtest_result(result)
    pnls = [trade.net_pnl for trade in result.trades]
    return {
        "initial_balance": result.initial_balance,
        "final_balance": result.final_balance,
        "net_pnl": result.net_pnl,
        "trades": len(result.trades),
        "win_rate": win_rate(pnls),
        "profit_factor": profit_factor(pnls),
        "max_drawdown": max_drawdown(result.equity_curve),
        "consistency": {
            "valid": consistency.valid,
            "issues": list(consistency.issues),
        },
    }
