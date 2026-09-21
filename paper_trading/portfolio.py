"""Portafolio virtual para paper trading."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real

from backtesting.models import PositionSide, calculate_gross_pnl


@dataclass
class VirtualPosition:
    side: PositionSide
    entry_price: float
    quantity: float
    stop_loss: float | None = None


class PaperPortfolio:
    """Mantiene una sola posición virtual y nunca comunica con un broker."""

    def __init__(self, initial_balance: float = 10_000.0, commission: float = 0.0, spread: float = 0.0) -> None:
        if isinstance(initial_balance, bool) or not isinstance(initial_balance, Real) or not isfinite(float(initial_balance)) or initial_balance <= 0:
            raise ValueError("initial_balance debe ser numérico, finito y mayor que 0")
        if any(isinstance(value, bool) or not isinstance(value, Real) or not isfinite(float(value)) or value < 0 for value in (commission, spread)):
            raise ValueError("commission y spread deben ser numéricos, finitos y no negativos")
        self.initial_balance = float(initial_balance)
        self.commission = float(commission)
        self.spread = float(spread)
        self.balance = self.initial_balance
        self.position: VirtualPosition | None = None

    def execution_entry_price(self, side: PositionSide, price: float) -> float:
        """Convierte precio de mercado a precio efectivo de entrada con spread."""
        if not isinstance(side, PositionSide):
            raise ValueError("side debe ser PositionSide")
        if isinstance(price, bool) or not isinstance(price, Real) or not isfinite(float(price)) or price <= 0:
            raise ValueError("price debe ser numérico, finito y mayor que 0")
        execution_price = (
            float(price) + self.spread / 2
            if side is PositionSide.BUY
            else float(price) - self.spread / 2
        )
        if execution_price <= 0:
            raise ValueError("el precio de ejecución resultante debe ser mayor que 0")
        return execution_price

    def open_position(self, side: PositionSide, price: float, quantity: float, stop_loss: float | None = None) -> None:
        if not isinstance(side, PositionSide):
            raise ValueError("side debe ser PositionSide")
        if self.position is not None:
            raise ValueError("Ya existe una posición abierta")
        if any(isinstance(value, bool) or not isinstance(value, Real) or not isfinite(float(value)) for value in (price, quantity)):
            raise ValueError("price y quantity deben ser numéricos y finitos")
        if price <= 0 or quantity <= 0:
            raise ValueError("price y quantity deben ser mayores que 0")
        if stop_loss is not None:
            if isinstance(stop_loss, bool) or not isinstance(stop_loss, Real) or not isfinite(float(stop_loss)) or stop_loss <= 0:
                raise ValueError("stop_loss debe ser numérico, finito y mayor que 0")
            stop_loss = float(stop_loss)
        execution_price = float(price) + self.spread / 2 if side is PositionSide.BUY else float(price) - self.spread / 2
        if execution_price <= 0:
            raise ValueError("el precio de ejecución resultante debe ser mayor que 0")
        if stop_loss is not None:
            if side is PositionSide.BUY and stop_loss >= execution_price:
                raise ValueError("stop_loss de BUY debe estar por debajo del precio")
            if side is PositionSide.SELL and stop_loss <= execution_price:
                raise ValueError("stop_loss de SELL debe estar por encima del precio")
        self.position = VirtualPosition(side, execution_price, float(quantity), stop_loss)

    def close_position(self, price: float) -> float:
        if self.position is None:
            raise ValueError("No existe una posición abierta")
        if isinstance(price, bool) or not isinstance(price, Real) or not isfinite(float(price)) or price <= 0:
            raise ValueError("price debe ser numérico, finito y mayor que 0")
        execution_price = float(price) - self.spread / 2 if self.position.side is PositionSide.BUY else float(price) + self.spread / 2
        gross_pnl = calculate_gross_pnl(self.position.side, self.position.entry_price, execution_price, self.position.quantity)
        pnl = gross_pnl - self.commission
        self.balance += pnl
        self.position = None
        return pnl

    def unrealized_pnl(self, price: float) -> float:
        if isinstance(price, bool) or not isinstance(price, Real) or not isfinite(float(price)) or price <= 0:
            raise ValueError("price debe ser numérico, finito y mayor que 0")
        if self.position is None:
            return 0.0
        execution_price = float(price) - self.spread / 2 if self.position.side is PositionSide.BUY else float(price) + self.spread / 2
        return calculate_gross_pnl(self.position.side, self.position.entry_price, execution_price, self.position.quantity)

    def mark_to_market(self, price: float) -> float:
        if isinstance(price, bool) or not isinstance(price, Real) or not isfinite(float(price)) or price <= 0:
            raise ValueError("price debe ser numérico, finito y mayor que 0")
        return self.balance + self.unrealized_pnl(price)
