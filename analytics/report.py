"""Resumen auditable de resultados de backtesting y paper trading."""

from __future__ import annotations

from dataclasses import dataclass

from backtesting.metrics import max_drawdown, profit_factor, win_rate
from backtesting.models import BacktestResult


@dataclass(frozen=True)
class PerformanceReport:
    """Métricas principales de una simulación."""

    initial_balance: float
    final_balance: float
    net_pnl: float
    trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float


def build_report(result: BacktestResult) -> PerformanceReport:
    """Convierte un resultado de backtest en métricas comparables."""
    pnls = [trade.net_pnl for trade in result.trades]
    return PerformanceReport(
        initial_balance=result.initial_balance,
        final_balance=result.final_balance,
        net_pnl=result.net_pnl,
        trades=len(result.trades),
        win_rate=win_rate(pnls),
        profit_factor=profit_factor(pnls),
        max_drawdown=max_drawdown(result.equity_curve),
    )
