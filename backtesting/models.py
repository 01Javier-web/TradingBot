"""Modelos de dominio para backtesting en modo simulación."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PositionSide(str, Enum):
    """Dirección de una posición simulada."""

    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Trade:
    """Operación cerrada generada por el motor de backtesting."""

    entry_time: object
    exit_time: object
    side: PositionSide
    entry_price: float
    exit_price: float
    quantity: float
    gross_pnl: float
    costs: float

    @property
    def net_pnl(self) -> float:
        """Resultado después de costes."""
        return self.gross_pnl - self.costs


@dataclass(frozen=True)
class BacktestResult:
    """Resultado agregado de una simulación."""

    initial_balance: float
    final_balance: float
    trades: tuple[Trade, ...]
    equity_curve: tuple[float, ...]

    @property
    def net_pnl(self) -> float:
        return self.final_balance - self.initial_balance
