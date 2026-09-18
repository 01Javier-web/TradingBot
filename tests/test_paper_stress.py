"""Pruebas de escenarios de estrés de paper trading."""

import pandas as pd

from paper_trading.stress import (
    default_stress_scenarios,
    run_default_stress_suite,
    run_stress_scenario,
)


def test_default_stress_suite_is_deterministic() -> None:
    first = run_default_stress_suite()
    second = run_default_stress_suite()

    assert first == second
    assert set(first) == {scenario.name for scenario in default_stress_scenarios()}


def test_opposite_signal_closes_virtual_position() -> None:
    scenario = next(item for item in default_stress_scenarios() if item.name == "opposite_signal")
    result = run_stress_scenario(scenario)

    assert result[0] == "OPEN BUY"
    assert result[1].startswith("CLOSE BUY:")
    assert result == scenario.expected_actions


def test_kill_switch_prevents_market_action() -> None:
    scenario = next(item for item in default_stress_scenarios() if item.name == "kill_switch")
    result = run_stress_scenario(scenario)

    assert result == scenario.expected_actions
    assert "OPEN" not in result[0]
    assert "CLOSE" not in result[0]


def test_stress_scenarios_are_small_and_timestamped() -> None:
    for scenario in default_stress_scenarios():
        assert scenario.rows
        assert all(pd.Timestamp(row["time"]).tz is None for row in scenario.rows)
