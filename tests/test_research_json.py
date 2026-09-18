"""Pruebas del exportador completo de investigación."""

from pathlib import Path

from ai.research_pipeline import run_research
from analytics.research_json import research_run_to_dict, save_research_run
from app.research_demo import synthetic_data
from backtesting.optimizer import ParameterGrid


def _run():
    return run_research(
        synthetic_data(80),
        ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)),
    )


def test_research_run_to_dict_contains_audit_sections() -> None:
    document = research_run_to_dict(_run())

    assert set(document) == {
        "experiment_id",
        "manifest",
        "finding",
        "validation",
        "quality",
        "decision",
        "candidates",
    }
    assert len(document["experiment_id"]) == 64
    assert document["manifest"]["rows"] == 80
    assert document["manifest"]["train_ratio"] == 0.7
    assert len(document["manifest"]["data_fingerprint"]) == 64
    assert document["finding"]["experiments"] == 1
    assert document["validation"]["valid"] is True
    assert document["quality"]["sample_size"] == 1
    assert document["quality"]["finite_results"] is True
    assert document["decision"]["execution_authorized"] is False
    assert document["decision"]["mode"] == "simulation-first"
    assert len(document["candidates"]) == 1


def test_save_research_run_writes_valid_json(tmp_path: Path) -> None:
    destination = tmp_path / "research" / "run.json"

    save_research_run(_run(), destination)

    assert destination.exists()
    content = destination.read_text(encoding="utf-8")
    assert '"experiment_id"' in content
    assert '"manifest"' in content
    assert '"finding"' in content
    assert '"quality"' in content
    assert '"decision"' in content


def test_research_json_is_deterministic(tmp_path: Path) -> None:
    run = _run()
    path = tmp_path / "run.json"
    save_research_run(run, path)
    first = path.read_text(encoding="utf-8")
    save_research_run(run, path)
    assert path.read_text(encoding="utf-8") == first
