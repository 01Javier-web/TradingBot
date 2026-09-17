"""Reporte de rendimiento para simulaciones de paper trading."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf, isfinite
from typing import Iterable

from paper_trading.portfolio import PaperPortfolio


_CLOSED_ACTIONS = frozenset({"CLOSE", "STOP_LOSS"})


@dataclass(frozen=True)
class PaperPerformanceReport:
    """Métricas realizadas de una sesión de paper trading."""

    initial_balance: float
    final_balance: float
    realized_pnl: float
    closed_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    open_position: bool
    consistent: bool
    consistency_issue: str | None


def _closed_pnls(events: Iterable[dict[str, object]]) -> list[float]:
    """Extrae únicamente PnL de eventos que cierran una posición."""
    pnls: list[float] = []
    for event in events:
        if event.get("action") not in _CLOSED_ACTIONS:
            continue
        pnl = event.get("pnl")
        if isinstance(pnl, bool):
            continue
        try:
            value = float(pnl)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        if isfinite(value):
            pnls.append(value)
    return pnls


def build_paper_report(
    portfolio: PaperPortfolio,
    events: Iterable[dict[str, object]],
    initial_balance: float,
) -> PaperPerformanceReport:
    """Construye métricas y comprueba balance inicial + PnL realizado."""
    if not isfinite(initial_balance) or initial_balance <= 0:
        raise ValueError("initial_balance debe ser finito y mayor que 0")

    pnls = _closed_pnls(events)
    realized_pnl = sum(pnls)
    final_balance = portfolio.balance
    expected_balance = float(initial_balance) + realized_pnl
    consistent = abs(final_balance - expected_balance) <= 1e-9
    issue = None if consistent else "final_balance no coincide con initial_balance + realized_pnl."

    gains = sum(pnl for pnl in pnls if pnl > 0)
    losses = -sum(pnl for pnl in pnls if pnl < 0)
    if losses == 0:
        factor = inf if gains > 0 else 0.0
    else:
        factor = gains / losses

    closed_trades = len(pnls)
    winning_trades = sum(pnl > 0 for pnl in pnls)
    losing_trades = sum(pnl < 0 for pnl in pnls)

    return PaperPerformanceReport(
        initial_balance=float(initial_balance),
        final_balance=final_balance,
        realized_pnl=realized_pnl,
        closed_trades=closed_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=winning_trades / closed_trades if closed_trades else 0.0,
        profit_factor=factor,
        open_position=portfolio.position is not None,
        consistent=consistent,
        consistency_issue=issue,
    )
