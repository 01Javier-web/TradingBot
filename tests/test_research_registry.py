"""Pruebas del registro persistente de investigaciones."""

from pathlib import Path

import pytest

from ai.research_pipeline import run_research
from analytics.research_registry import (
    compare_research_records,
    list_research_records,
    load_research_record,
    record_from_run,
    save_research_record,
)
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
    assert record.fast_ema_periods == (5,)


def test_save_research_record_uses_experiment_id(tmp_path: Path) -> None:
    run = _run()

    path = save_research_record(run, tmp_path / "research")

    assert path.name == f"{run.experiment_id}.json"
    assert path.exists()
    document = load_research_record(path)
    assert document["experiment_id"] == run.experiment_id
    assert document["manifest"]["data_fingerprint"] == run.manifest.data_fingerprint


def test_save_same_research_record_is_idempotent(tmp_path: Path) -> None:
    run = _run()
    directory = tmp_path / "research"

    first = save_research_record(run, directory)
    second = save_research_record(run, directory)

    assert first == second


def test_save_different_content_with_same_id_requires_overwrite(tmp_path: Path) -> None:
    run = _run()
    directory = tmp_path / "research"
    path = save_research_record(run, directory)
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match=run.experiment_id):
        save_research_record(run, directory)

    save_research_record(run, directory, overwrite=True)
    assert path.read_text(encoding="utf-8").endswith("}\n") is False


def test_list_research_records_returns_saved_runs(tmp_path: Path) -> None:
    run = _run()
    directory = tmp_path / "research"
    save_research_record(run, directory)

    records = list_research_records(directory)

    assert len(records) == 1
    assert records[0].experiment_id == run.experiment_id
    assert records[0].slow_ema_periods == (20,)


def test_list_missing_directory_is_empty(tmp_path: Path) -> None:
    assert list_research_records(tmp_path / "missing") == ()


def test_compare_research_records_describes_context() -> None:
    first = record_from_run(_run())
    second = record_from_run(
        run_research(
            synthetic_data(80),
            ParameterGrid(fast_ema_periods=(10,), slow_ema_periods=(20,), rsi_periods=(14,)),
        )
    )

    comparison = compare_research_records(first, second)

    assert comparison["same_data"] is True
    assert comparison["same_rows"] is True
    assert comparison["same_train_ratio"] is True
    assert comparison["same_fast_ema_grid"] is False
    assert comparison["same_slow_ema_grid"] is True
    assert comparison["same_rsi_grid"] is True
    assert comparison["first_experiment_id"] == first.experiment_id
    assert comparison["second_experiment_id"] == second.experiment_id
