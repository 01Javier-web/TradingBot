"""Pruebas de auditoría del catálogo."""

from pathlib import Path
import json

from analytics.research_audit import audit_catalog


def _document(experiment_id: str = "abc") -> dict:
    return {
        "experiment_id": experiment_id,
        "manifest": {
            "rows": 80,
            "train_ratio": 0.7,
            "data_fingerprint": "a" * 64,
            "fast_ema_periods": [5],
            "slow_ema_periods": [20],
            "rsi_periods": [14],
        },
    }


def test_audit_missing_directory_is_empty(tmp_path: Path) -> None:
    assert audit_catalog(tmp_path / "missing") == audit_catalog(tmp_path / "missing")
    result = audit_catalog(tmp_path / "missing")
    assert result.files == 0
    assert result.valid == 0
    assert result.invalid == 0


def test_audit_counts_invalid_record(tmp_path: Path) -> None:
    directory = tmp_path / "research"
    directory.mkdir()
    (directory / "valid.json").write_text(json.dumps(_document()), encoding="utf-8")
    invalid = _document()
    invalid["manifest"]["train_ratio"] = 0.8
    (directory / "invalid.json").write_text(json.dumps(invalid), encoding="utf-8")

    result = audit_catalog(directory)

    assert result.files == 2
    assert result.valid == 0
    assert result.invalid == 2
    assert len(result.issues) == 2
