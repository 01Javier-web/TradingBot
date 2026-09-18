"""Escenarios deterministas de estrés para paper trading.

Los escenarios ejercitan límites de riesgo, stop-loss, kill switch y señales
contrarias sin depender de MetaTrader 5 ni de ejecución real.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from risk.kill_switch import KillSwitch
from risk.manager import RiskConfig, RiskManager
from strategy.signals import Signal


@dataclass(frozen=True)
class StressScenario:
    name: str
    rows: tuple[dict[str, object], ...]
    expected_actions: tuple[str, ...]


def _rows(values: tuple[tuple[float, Signal, float], ...]) -> tuple[dict[str, object], ...]:
    return tuple(
        {"time": pd.Timestamp("2026-01-01") + pd.Timedelta(minutes=index),
         "open": price, "high": price + 1, "low": max(0.1, price - 1),
         "close": price, "signal": signal, "atr": atr_value}
        for index, (price, signal, atr_value) in enumerate(values)
    )


def default_stress_scenarios() -> tuple[StressScenario, ...]:
    """Devuelve escenarios pequeños y reproducibles para revisión de seguridad."""
    return (
        StressScenario(
            "opposite_signal",
            _rows(((100.0, Signal.BUY, 2.0), (101.0, Signal.SELL, 2.0))),
            ("OPEN BUY", "CLOSE BUY: pnl=1.000000"),
        ),
        StressScenario(
            "stop_loss",
            _rows(((100.0, Signal.BUY, 2.0), (97.0, Signal.WAIT, 2.0))),
            ("OPEN BUY", "STOP_LOSS BUY: pnl=-2.000000"),
        ),
        StressScenario(
            "kill_switch",
            _rows(((100.0, Signal.WAIT, 2.0),)),
            ("STOPPED: Kill switch activo: emergency"),
        ),
        StressScenario(
            "risk_limit",
            _rows(((100.0, Signal.BUY, 500.0),)),
            ("REJECTED: supera el riesgo máximo por operación",),
        ),
    )


def run_stress_scenario(scenario: StressScenario) -> tuple[str, ...]:
    """Ejecuta un escenario aislado en un portafolio virtual."""
    kill_switch = KillSwitch()
    if scenario.name == "kill_switch":
        kill_switch.trigger("emergency")

    risk = RiskManager(RiskConfig(max_risk_per_trade=0.01, max_daily_loss=0.02))
    engine = PaperTradingEngine(
        PaperPortfolio(initial_balance=10_000.0),
        risk_manager=risk,
        quantity=1.0,
        kill_switch=kill_switch,
    )
    return tuple(engine.process(pd.Series(row)) for row in scenario.rows)


def run_default_stress_suite() -> dict[str, tuple[str, ...]]:
    """Ejecuta toda la suite determinista y devuelve solo resultados observables."""
    return {scenario.name: run_stress_scenario(scenario) for scenario in default_stress_scenarios()}


__all__ = [
    "StressScenario",
    "default_stress_scenarios",
    "run_stress_scenario",
    "run_default_stress_suite",
]
