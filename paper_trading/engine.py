"""Motor de paper trading basado en señales ya calculadas."""

from __future__ import annotations

from math import isfinite

import pandas as pd

from backtesting.models import PositionSide
from paper_trading.portfolio import PaperPortfolio
from risk.kill_switch import KillSwitch
from risk.manager import RiskManager
from strategy.signals import Signal


class PaperTradingEngine:
    """Procesa velas secuencialmente sin enviar ninguna orden a MT5."""

    def __init__(self, portfolio: PaperPortfolio, risk_manager: RiskManager | None = None, quantity: float = 1.0, kill_switch: KillSwitch | None = None) -> None:
        if not isfinite(quantity) or quantity <= 0:
            raise ValueError("quantity debe ser finito y mayor que 0")
        self.portfolio = portfolio
        self.risk_manager = risk_manager or RiskManager()
        self.quantity = float(quantity)
        self.kill_switch = kill_switch or KillSwitch()
        self.daily_loss = 0.0
        self.history: list[dict[str, object]] = []

    def process(self, row: pd.Series) -> str:
        """Procesa una vela; datos inválidos no generan acciones de mercado."""
        if self.kill_switch.active:
            reason = self.kill_switch.reason or "sin motivo especificado"
            self.history.append({"action": "KILL_SWITCH", "reason": reason})
            return f"STOPPED: Kill switch activo: {reason}"

        try:
            price = float(row["close"])
        except (KeyError, TypeError, ValueError):
            self.history.append({"action": "REJECTED", "reason": "precio inválido"})
            return "WAIT: precio inválido"
        if not isfinite(price) or price <= 0:
            self.history.append({"action": "REJECTED", "reason": "precio inválido"})
            return "WAIT: precio inválido"

        if self.portfolio.position is not None:
            position = self.portfolio.position
            hit_stop = (
                position.stop_loss is not None
                and ((position.side is PositionSide.BUY and price <= position.stop_loss)
                     or (position.side is PositionSide.SELL and price >= position.stop_loss))
            )
            if hit_stop:
                pnl = self.portfolio.close_position(position.stop_loss)
                self.daily_loss += max(0.0, -pnl)
                self.history.append({"action": "STOP_LOSS", "price": position.stop_loss, "pnl": pnl})
                return f"STOP_LOSS {position.side.value}: pnl={pnl:.6f}"

        signal = row.get("signal", Signal.WAIT)
        if isinstance(signal, str):
            try:
                signal = Signal(signal)
            except ValueError:
                self.history.append({"action": "REJECTED", "reason": "señal inválida"})
                return "WAIT: señal inválida"
        if not isinstance(signal, Signal):
            self.history.append({"action": "REJECTED", "reason": "señal inválida"})
            return "WAIT: señal inválida"

        if self.portfolio.position is None and signal in (Signal.BUY, Signal.SELL):
            side = PositionSide(signal.value)
            try:
                raw_atr = float(row.get("atr", 0.0))
            except (TypeError, ValueError):
                self.history.append({"action": "REJECTED", "reason": "ATR inválido"})
                return "WAIT: ATR inválido"
            if not isfinite(raw_atr):
                self.history.append({"action": "REJECTED", "reason": "ATR inválido"})
                return "WAIT: ATR inválido"
            stop_distance = abs(raw_atr)
            decision = self.risk_manager.approve(
                balance=self.portfolio.balance,
                risk_amount=stop_distance * self.quantity,
                daily_loss=self.daily_loss,
                open_positions=0,
                stop_loss_distance=stop_distance,
            )
            if not decision.approved:
                self.history.append({"action": "REJECTED", "reason": decision.reason})
                return f"REJECTED: {decision.reason}"
            stop_loss = price - stop_distance if side is PositionSide.BUY else price + stop_distance
            if not isfinite(stop_loss) or stop_loss <= 0:
                reason = "stop-loss calculado inválido"
                self.history.append({"action": "REJECTED", "reason": reason})
                return f"REJECTED: {reason}"
            self.portfolio.open_position(side, price, self.quantity, stop_loss)
            self.history.append({"action": "OPEN", "side": side.value, "price": price, "stop_loss": stop_loss})
            return f"OPEN {side.value}"

        if self.portfolio.position is not None and signal in (Signal.BUY, Signal.SELL):
            current = self.portfolio.position.side
            if signal.value != current.value:
                pnl = self.portfolio.close_position(price)
                self.daily_loss += max(0.0, -pnl)
                self.history.append({"action": "CLOSE", "side": current.value, "price": price, "pnl": pnl})
                return f"CLOSE {current.value}: pnl={pnl:.6f}"

        return "WAIT"
