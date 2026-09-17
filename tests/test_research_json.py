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

    assert set(document) == {"finding", "validation", "candidates"}
    assert document["finding"]["experiments"] == 1
    assert document["validation"]["valid"] is True
    assert len(document["candidates"]) == 1


def test_save_research_run_writes_valid_json(tmp_path: Path) -> None:
    destination = tmp_path / "research" / "run.json"

    save_research_run(_run(), destination)

    assert destination.exists()
    assert '"finding"' in destination.read_text(encoding="utf-8")
