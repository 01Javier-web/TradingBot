"""Pruebas del pipeline reproducible de investigación."""

import pandas as pd

from ai.research_pipeline import run_research
from backtesting.optimizer import ParameterGrid


def _data(rows: int = 80) -> pd.DataFrame:
    close = pd.Series(range(1, rows + 1), dtype=float)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="15min"),
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
        }
    )


def test_research_pipeline_returns_results_and_finding() -> None:
    run = run_research(
        _data(),
        ParameterGrid(fast_ema_periods=(5, 10), slow_ema_periods=(20, 30), rsi_periods=(14,)),
    )

    assert len(run.results) == 4
    assert run.finding.experiments == 4
    assert run.finding.profitable_train >= 0
    assert run.finding.profitable_test >= 0
    assert run.manifest.rows == 80
    assert run.manifest.train_ratio == 0.7
    assert len(run.manifest.data_fingerprint) == 64


def test_research_pipeline_preserves_optimizer_order() -> None:
    run = run_research(
        _data(),
        ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)),
    )

    assert len(run.results) == 1
    assert run.results[0].config.fast_ema_period == 5
    assert run.results[0].config.slow_ema_period == 20


def test_research_pipeline_records_custom_train_ratio() -> None:
    run = run_research(
        _data(),
        ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)),
        train_ratio=0.75,
    )

    assert run.manifest.train_ratio == 0.75
