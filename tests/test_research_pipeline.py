"""Pruebas del pipeline reproducible de investigación."""

import pandas as pd

from ai.research_pipeline import run_research
from backtesting.optimizer import ParameterGrid


def _data(rows: int = 80) -> pd.DataFrame:
    close = pd.Series(range(1, rows + 1), dtype=float)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="15min", tz="UTC"),
            "open": close,
            "high": close + 1,
            "low": (close - 1).clip(lower=0.1),
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


def test_research_pipeline_has_stable_experiment_identity() -> None:
    grid = ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,))
    first = run_research(_data(), grid)
    second = run_research(_data(), grid)

    assert first.experiment_id == second.experiment_id
    assert first.manifest.schema_version == "research-v1"


def test_research_identity_changes_when_manifest_schema_changes() -> None:
    from analytics.research_id import build_experiment_id
    from analytics.research_manifest import ResearchManifest

    grid = ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,))
    run = run_research(_data(), grid)
    changed = ResearchManifest(
        rows=run.manifest.rows,
        train_ratio=run.manifest.train_ratio,
        data_fingerprint=run.manifest.data_fingerprint,
        fast_ema_periods=run.manifest.fast_ema_periods,
        slow_ema_periods=run.manifest.slow_ema_periods,
        rsi_periods=run.manifest.rsi_periods,
        schema_version="research-v2",
    )
    assert build_experiment_id(changed) != run.experiment_id



def test_research_run_rejects_mismatched_experiment_identity() -> None:
    import pytest
    from ai.research_pipeline import ResearchRun

    run = run_research(_data(), ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)))
    with pytest.raises(ValueError, match="experiment_id"):
        ResearchRun(run.results, run.finding, run.evidence, run.manifest, "0" * 64)


def test_research_run_rejects_inconsistent_finding() -> None:
    import pytest
    from ai.research_pipeline import ResearchRun
    from ai.researcher import ResearchFinding

    run = run_research(_data(), ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)))
    finding = ResearchFinding(99, run.finding.profitable_train, run.finding.profitable_test,
                              run.finding.generalization_rate, run.finding.findings)
    with pytest.raises(ValueError, match="finding.experiments"):
        ResearchRun(run.results, finding, run.evidence, run.manifest, run.experiment_id)
