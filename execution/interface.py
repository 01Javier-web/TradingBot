"""Contrato común para adaptadores de ejecución."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Protocol


class ExecutionSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class ExecutionRequest:
    """Solicitud de ejecución validada por capas superiores."""

    symbol: str
    side: ExecutionSide
    quantity: float
    stop_loss: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("symbol no puede estar vacío")
        if not isinstance(self.side, ExecutionSide):
            raise ValueError("side debe ser ExecutionSide")
        if isinstance(self.quantity, bool) or not isfinite(float(self.quantity)) or self.quantity <= 0:
            raise ValueError("quantity debe ser finito y mayor que 0")
        if self.stop_loss is not None and (
            isinstance(self.stop_loss, bool) or not isfinite(float(self.stop_loss)) or self.stop_loss <= 0
        ):
            raise ValueError("stop_loss debe ser finito y mayor que 0")


@dataclass(frozen=True)
class ExecutionResult:
    accepted: bool
    message: str
    broker_order_id: str | None = None


class ExecutionAdapter(Protocol):
    """Contrato que deben cumplir los adaptadores de ejecución."""

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        ...
