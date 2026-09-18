"""Modelos de dominio para backtesting en modo simulación."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from numbers import Real


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

    def __post_init__(self) -> None:
        if not isinstance(self.side, PositionSide):
            raise ValueError("side debe ser PositionSide")
        numeric = (self.entry_price, self.exit_price, self.quantity, self.gross_pnl, self.costs)
        if any(isinstance(value, bool) or not isinstance(value, Real) for value in numeric):
            raise ValueError("Los campos numéricos del trade deben ser numéricos")
        if not all(isfinite(float(value)) for value in numeric):
            raise ValueError("Los campos numéricos del trade deben ser finitos")

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

    def __post_init__(self) -> None:
        numeric = (self.initial_balance, self.final_balance)
        if any(isinstance(value, bool) or not isinstance(value, Real) for value in numeric):
            raise ValueError("Los balances deben ser numéricos")
        if not all(isfinite(float(value)) for value in numeric):
            raise ValueError("Los balances deben ser finitos")
        if not self.equity_curve:
            raise ValueError("equity_curve no puede estar vacía")
        if any(
            isinstance(value, bool)
            or not isinstance(value, Real)
            or not isfinite(float(value))
            for value in self.equity_curve
        ):
            raise ValueError("equity_curve debe contener valores finitos")
        if any(not isinstance(trade, Trade) for trade in self.trades):
            raise ValueError("trades debe contener únicamente Trade")

    @property
    def net_pnl(self) -> float:
        return self.final_balance - self.initial_balance


__all__ = ["BacktestResult", "PositionSide", "Trade"]
