"""Pruebas del registro persistente de investigaciones."""

from pathlib import Path

from ai.research_pipeline import run_research
from analytics.research_registry import load_research_record, record_from_run, save_research_record
from app.research_demo import synthetic_data
from backtesting.optimizer import ParameterGrid


def _run():
    return run_research(
        synthetic_data(80),
        ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)),
    )


def test_record_from_run_keeps_experiment_identity() -> None:
    run = _run()
    record = record_from_run(run)

    assert record.experiment_id == run.experiment_id
    assert record.data_fingerprint == run.manifest.data_fingerprint
    assert record.rows == 80
    assert record.train_ratio == 0.7


def test_save_research_record_uses_experiment_id(tmp_path: Path) -> None:
    run = _run()

    path = save_research_record(run, tmp_path / "research")

    assert path.name == f"{run.experiment_id}.json"
    assert path.exists()
    document = load_research_record(path)
    assert document["experiment_id"] == run.experiment_id
    assert document["manifest"]["data_fingerprint"] == run.manifest.data_fingerprint
