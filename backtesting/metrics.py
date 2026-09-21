"""Métricas básicas de evaluación de backtests."""

from __future__ import annotations

from math import inf, isfinite
from numbers import Real


def _finite_values(values: list[float] | tuple[float, ...]) -> tuple[float, ...]:
    if not isinstance(values, (list, tuple)):
        raise TypeError("La serie debe ser list o tuple")
    if any(isinstance(value, bool) or not isinstance(value, Real) for value in values):
        raise ValueError("Las métricas requieren valores numéricos")
    normalized = tuple(float(value) for value in values)
    if not all(isfinite(value) for value in normalized):
        raise ValueError("Las métricas requieren valores finitos")
    return normalized


def max_drawdown(equity_curve: list[float] | tuple[float, ...]) -> float:
    """Devuelve el drawdown máximo como proporción del pico de equity."""
    values = _finite_values(equity_curve)
    if not values:
        return 0.0
    if values[0] <= 0:
        raise ValueError("La equity inicial debe ser mayor que 0")
    peak = values[0]
    maximum = 0.0
    for value in values:
        if value > peak:
            peak = value
        if peak > 0:
            maximum = max(maximum, (peak - value) / peak)
    return maximum


def win_rate(net_pnls: list[float] | tuple[float, ...]) -> float:
    """Porcentaje de operaciones con resultado neto positivo."""
    values = _finite_values(net_pnls)
    if not values:
        return 0.0
    return sum(pnl > 0 for pnl in values) / len(values)


def profit_factor(net_pnls: list[float] | tuple[float, ...]) -> float:
    """Ganancias brutas divididas por pérdidas brutas."""
    values = _finite_values(net_pnls)
    gains = sum(pnl for pnl in values if pnl > 0)
    losses = -sum(pnl for pnl in values if pnl < 0)
    if losses == 0:
        return inf if gains > 0 else 0.0
    return gains / losses
