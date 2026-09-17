"""Escenarios predefinidos para pruebas de simulación."""

from __future__ import annotations

from dataclasses import dataclass

from backtesting.engine import BacktestEngine
from strategy.signals import StrategyConfig


@dataclass(frozen=True)
class BacktestScenario:
    name: str
    strategy: StrategyConfig
    initial_balance: float = 10_000.0
    quantity: float = 1.0
    commission: float = 0.0
    spread: float = 0.0

    def build_engine(self) -> BacktestEngine:
        return BacktestEngine(
            initial_balance=self.initial_balance,
            quantity=self.quantity,
            commission=self.commission,
            spread=self.spread,
        )


BASELINE = BacktestScenario("baseline", StrategyConfig())
