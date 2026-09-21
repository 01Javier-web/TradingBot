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


def calculate_gross_pnl(
    side: PositionSide,
    entry_price: float,
    exit_price: float,
    quantity: float,
) -> float:
    """Calcula PnL bruto con la misma convención BUY/SELL en todo el sistema."""
    if not isinstance(side, PositionSide):
        raise ValueError("side debe ser PositionSide")
    values = (entry_price, exit_price, quantity)
    if any(isinstance(value, bool) or not isinstance(value, Real) or not isfinite(float(value)) for value in values):
        raise ValueError("Los valores de PnL deben ser numéricos y finitos")
    if entry_price <= 0 or exit_price <= 0 or quantity <= 0:
        raise ValueError("precios y quantity deben ser mayores que 0")
    direction = 1.0 if side is PositionSide.BUY else -1.0
    return (float(exit_price) - float(entry_price)) * direction * float(quantity)


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
        if self.entry_price <= 0 or self.exit_price <= 0:
            raise ValueError("Los precios del trade deben ser positivos")
        if self.quantity <= 0:
            raise ValueError("quantity debe ser positiva")
        if self.costs < 0:
            raise ValueError("costs no puede ser negativo")
        try:
            if self.entry_time >= self.exit_time:
                raise ValueError("exit_time debe ser posterior a entry_time")
        except TypeError as exc:
            raise ValueError("timestamps del trade no son comparables") from exc

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
        if self.initial_balance <= 0:
            raise ValueError("initial_balance debe ser positivo")
        if self.equity_curve[0] != self.initial_balance:
            raise ValueError("La curva de equity debe comenzar con initial_balance")
        if self.equity_curve[-1] != self.final_balance:
            raise ValueError("La curva de equity debe terminar con final_balance")
        calculated = self.initial_balance + sum(trade.net_pnl for trade in self.trades)
        if abs(calculated - self.final_balance) > 1e-8:
            raise ValueError("final_balance no coincide con la suma de los resultados de las operaciones")

    @property
    def net_pnl(self) -> float:
        return self.final_balance - self.initial_balance


__all__ = ["BacktestResult", "PositionSide", "Trade", "calculate_gross_pnl"]
