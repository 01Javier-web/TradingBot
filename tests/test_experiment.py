"""Pruebas de experimentos reproducibles."""

import pandas as pd

from backtesting.experiment import Experiment, ExperimentRunner
from strategy.signals import StrategyConfig


def make_data() -> pd.DataFrame:
    close = [100 + i * 0.2 for i in range(80)]
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=len(close), freq="15min"),
            "open": close,
            "high": [value + 0.2 for value in close],
            "low": [value - 0.2 for value in close],
            "close": close,
        }
    )


def test_experiment_runner_returns_report() -> None:
    experiment = Experiment("baseline", StrategyConfig(fast_ema_period=5, slow_ema_period=10))
    report = ExperimentRunner().run(make_data(), experiment)
    assert report.initial_balance == 10_000
    assert report.trades >= 0


def test_experiment_definition_can_be_saved(tmp_path) -> None:
    experiment = Experiment("baseline", StrategyConfig())
    path = tmp_path / "baseline.json"
    ExperimentRunner.save_definition(experiment, path)
    content = path.read_text(encoding="utf-8")
    assert '"name": "baseline"' in content
    assert '"fast_ema_period": 20' in content
