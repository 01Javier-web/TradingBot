"""Pruebas de sensibilidad a costes de ejecución."""

import pandas as pd
import pytest

from backtesting.stress import StressScenario, run_stress_scenario
from strategy.signals import StrategyConfig


def make_data() -> pd.DataFrame:
    close = [100 + i * 0.2 for i in range(80)]
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=80, freq="15min"),
            "open": close,
            "high": [x + 0.2 for x in close],
            "low": [x - 0.2 for x in close],
            "close": close,
        }
    )


def test_stress_scenario_applies_costs() -> None:
    strategy = StrategyConfig(fast_ema_period=5, slow_ema_period=10)
    clean = run_stress_scenario(make_data(), strategy, StressScenario("clean"))
    stressed = run_stress_scenario(
        make_data(), strategy, StressScenario("stressed", commission=2.0, spread=0.5)
    )
    assert stressed.net_pnl <= clean.net_pnl


def test_stress_scenario_rejects_negative_costs() -> None:
    with pytest.raises(ValueError):
        StressScenario("invalid", spread=-1)
