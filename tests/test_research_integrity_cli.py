"""Pruebas del auditor CLI de investigaciones."""

import json
from pathlib import Path

from app.research_integrity_cli import audit_directory, format_audit


def _document(experiment_id: str = "bad") -> dict:
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


def test_audit_directory_reports_invalid_json_identity(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(_document()), encoding="utf-8")

    results = audit_directory(tmp_path)
    output = format_audit(results)

    assert results[0][1] is False
    assert "Inválidos: 1" in output
    assert "bad.json" in output


def test_audit_directory_returns_empty_for_missing_directory(tmp_path: Path) -> None:
    assert audit_directory(tmp_path / "missing") == ()


def test_format_audit_reports_valid_count() -> None:
    output = format_audit((("ok.json", True, ()), ("bad.json", False, ("problema",))))

    assert "Registros: 2" in output
    assert "Válidos: 1" in output
    assert "Inválidos: 1" in output
    assert "problema" in output
