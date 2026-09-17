"""Adaptador de ejecución contra el portafolio virtual."""

from __future__ import annotations

from backtesting.models import PositionSide
from paper_trading.portfolio import PaperPortfolio
from execution.interface import ExecutionRequest, ExecutionResult, ExecutionSide


class PaperExecutionAdapter:
    """Implementación local que nunca contacta un broker."""

    def __init__(self, portfolio: PaperPortfolio) -> None:
        self.portfolio = portfolio

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        side = PositionSide.BUY if request.side is ExecutionSide.BUY else PositionSide.SELL
        if self.portfolio.position is not None:
            return ExecutionResult(False, "ya existe una posición virtual abierta")
        # El adaptador requiere un precio explícito del mercado antes de abrir.
        return ExecutionResult(False, f"paper adapter requiere precio para {side.value}")
