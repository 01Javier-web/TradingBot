"""Contrato común para adaptadores de ejecución."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
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
        if not self.symbol.strip():
            raise ValueError("symbol no puede estar vacío")
        if self.quantity <= 0:
            raise ValueError("quantity debe ser mayor que 0")
        if self.stop_loss is not None and self.stop_loss <= 0:
            raise ValueError("stop_loss debe ser mayor que 0")


@dataclass(frozen=True)
class ExecutionResult:
    accepted: bool
    message: str
    broker_order_id: str | None = None


class ExecutionAdapter(Protocol):
    """Contrato que deben cumplir los adaptadores de ejecución."""

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        ...
