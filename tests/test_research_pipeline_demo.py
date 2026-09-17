"""Pruebas del demo que persiste corridas de investigación."""

from pathlib import Path

from analytics.research_registry import list_research_records
from app import research_pipeline_demo


def test_demo_persists_research_run(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    research_pipeline_demo.main()

    records = list_research_records(tmp_path / "artifacts" / "research")

    assert len(records) == 1
    assert records[0].rows == 160
    assert records[0].train_ratio == 0.7
    assert records[0].fast_ema_periods == (5, 10)
    assert records[0].slow_ema_periods == (20, 30)
    assert records[0].rsi_periods == (14,)
    output = capsys.readouterr().out
    assert "Experiment ID:" in output
    assert "Registro:" in output
