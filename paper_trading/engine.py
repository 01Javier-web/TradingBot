"""Motor de paper trading basado en señales ya calculadas."""

from __future__ import annotations

import pandas as pd

from backtesting.models import PositionSide
from paper_trading.portfolio import PaperPortfolio
from risk.manager import RiskManager
from strategy.signals import Signal


class PaperTradingEngine:
    """Procesa velas secuencialmente sin enviar ninguna orden a MT5."""

    def __init__(self, portfolio: PaperPortfolio, risk_manager: RiskManager | None = None, quantity: float = 1.0) -> None:
        if quantity <= 0:
            raise ValueError("quantity debe ser mayor que 0")
        self.portfolio = portfolio
        self.risk_manager = risk_manager or RiskManager()
        self.quantity = float(quantity)

    def process(self, row: pd.Series) -> str:
        """Procesa una vela con columna ``signal`` y precio de cierre."""
        signal = row.get("signal", Signal.WAIT)
        if isinstance(signal, str):
            try:
                signal = Signal(signal)
            except ValueError:
                return "WAIT: señal inválida"
        price = float(row["close"])

        if self.portfolio.position is None and signal in (Signal.BUY, Signal.SELL):
            side = PositionSide(signal.value)
            stop_distance = abs(float(row.get("atr", 0.0)))
            decision = self.risk_manager.approve(
                balance=self.portfolio.balance,
                risk_amount=stop_distance * self.quantity,
                daily_loss=0.0,
                open_positions=0,
                stop_loss_distance=stop_distance,
            )
            if not decision.approved:
                return f"REJECTED: {decision.reason}"
            stop_loss = price - stop_distance if side is PositionSide.BUY else price + stop_distance
            self.portfolio.open_position(side, price, self.quantity, stop_loss)
            return f"OPEN {side.value}"

        if self.portfolio.position is not None and signal in (Signal.BUY, Signal.SELL):
            current = self.portfolio.position.side
            if signal.value != current.value:
                pnl = self.portfolio.close_position(price)
                return f"CLOSE {current.value}: pnl={pnl:.6f}"

        return "WAIT"
