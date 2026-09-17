"""Configuración centralizada y validada del entorno de simulación."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TradingConfig:
    """Parámetros operativos que no contienen secretos."""

    symbol: str = "EURUSD"
    timeframe: str = "M15"
    initial_balance: float = 10_000.0
    quantity: float = 1.0
    commission: float = 0.0
    spread: float = 0.0

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol no puede estar vacío")
        if not self.timeframe.strip():
            raise ValueError("timeframe no puede estar vacío")
        if self.initial_balance <= 0:
            raise ValueError("initial_balance debe ser mayor que 0")
        if self.quantity <= 0:
            raise ValueError("quantity debe ser mayor que 0")
        if self.commission < 0 or self.spread < 0:
            raise ValueError("commission y spread no pueden ser negativos")
