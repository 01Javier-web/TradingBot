"""Métricas básicas de evaluación de backtests."""

from __future__ import annotations

from math import inf


def max_drawdown(equity_curve: list[float] | tuple[float, ...]) -> float:
    """Devuelve el drawdown máximo como proporción del pico de equity."""
    if not equity_curve:
        return 0.0
    peak = float(equity_curve[0])
    maximum = 0.0
    for value in equity_curve:
        value = float(value)
        if value > peak:
            peak = value
        if peak > 0:
            maximum = max(maximum, (peak - value) / peak)
    return maximum


def win_rate(net_pnls: list[float] | tuple[float, ...]) -> float:
    """Porcentaje de operaciones con resultado neto positivo."""
    if not net_pnls:
        return 0.0
    return sum(pnl > 0 for pnl in net_pnls) / len(net_pnls)


def profit_factor(net_pnls: list[float] | tuple[float, ...]) -> float:
    """Ganancias brutas divididas por pérdidas brutas."""
    gains = sum(pnl for pnl in net_pnls if pnl > 0)
    losses = -sum(pnl for pnl in net_pnls if pnl < 0)
    if losses == 0:
        return inf if gains > 0 else 0.0
    return gains / losses
