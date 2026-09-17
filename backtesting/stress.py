"""Stress testing de backtests mediante costes de ejecución conservadores."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtesting.engine import BacktestEngine
from backtesting.models import BacktestResult
from strategy.signals import StrategyConfig


@dataclass(frozen=True)
class StressScenario:
    """Escenario de costes usado para una simulación de sensibilidad."""

    name: str
    commission: float = 0.0
    spread: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name no puede estar vacío")
        if self.commission < 0 or self.spread < 0:
            raise ValueError("commission y spread no pueden ser negativos")


def run_stress_scenario(
    df: pd.DataFrame,
    strategy: StrategyConfig,
    scenario: StressScenario,
    *,
    initial_balance: float = 10_000.0,
    quantity: float = 1.0,
) -> BacktestResult:
    """Ejecuta el mismo sistema bajo costes definidos por el escenario."""
    engine = BacktestEngine(
        initial_balance=initial_balance,
        quantity=quantity,
        commission=scenario.commission,
        spread=scenario.spread,
    )
    return engine.run(df, strategy)
