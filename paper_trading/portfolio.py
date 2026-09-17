"""Portafolio virtual para paper trading."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from backtesting.models import PositionSide


@dataclass
class VirtualPosition:
    side: PositionSide
    entry_price: float
    quantity: float
    stop_loss: float | None = None


class PaperPortfolio:
    """Mantiene una sola posición virtual y nunca comunica con un broker."""

    def __init__(self, initial_balance: float = 10_000.0) -> None:
        if not isfinite(initial_balance) or initial_balance <= 0:
            raise ValueError("initial_balance debe ser finito y mayor que 0")
        self.balance = float(initial_balance)
        self.position: VirtualPosition | None = None

    def open_position(self, side: PositionSide, price: float, quantity: float, stop_loss: float | None = None) -> None:
        if self.position is not None:
            raise ValueError("Ya existe una posición abierta")
        if not isfinite(price) or not isfinite(quantity) or price <= 0 or quantity <= 0:
            raise ValueError("price y quantity deben ser finitos y mayores que 0")
        if stop_loss is not None and (not isfinite(stop_loss) or stop_loss <= 0):
            raise ValueError("stop_loss debe ser finito y mayor que 0")
        self.position = VirtualPosition(side, float(price), float(quantity), stop_loss)

    def close_position(self, price: float) -> float:
        if self.position is None:
            raise ValueError("No existe una posición abierta")
        if not isfinite(price) or price <= 0:
            raise ValueError("price debe ser finito y mayor que 0")
        direction = 1 if self.position.side is PositionSide.BUY else -1
        pnl = (float(price) - self.position.entry_price) * direction * self.position.quantity
        self.balance += pnl
        self.position = None
        return pnl

    def mark_to_market(self, price: float) -> float:
        """Calcula equity virtual sin cerrar la posición."""
        if not isfinite(price) or price <= 0:
            raise ValueError("price debe ser finito y mayor que 0")
        if self.position is None:
            return self.balance
        direction = 1 if self.position.side is PositionSide.BUY else -1
        unrealized = (float(price) - self.position.entry_price) * direction * self.position.quantity
        return self.balance + unrealized
