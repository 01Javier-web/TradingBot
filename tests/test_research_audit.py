"""Pruebas de auditoría del catálogo."""

from pathlib import Path
import json

from analytics.research_audit import audit_catalog
from analytics.research_id import build_experiment_id
from analytics.research_manifest import ResearchManifest


def _document() -> dict:
    manifest = ResearchManifest(
        rows=80,
        train_ratio=0.7,
        data_fingerprint="a" * 64,
        fast_ema_periods=(5,),
        slow_ema_periods=(20,),
        rsi_periods=(14,),
    )
    return {
        "experiment_id": build_experiment_id(manifest),
        "manifest": {
            "rows": manifest.rows,
            "train_ratio": manifest.train_ratio,
            "data_fingerprint": manifest.data_fingerprint,
            "fast_ema_periods": list(manifest.fast_ema_periods),
            "slow_ema_periods": list(manifest.slow_ema_periods),
            "rsi_periods": list(manifest.rsi_periods),
        },
    }


def test_audit_missing_directory_is_empty(tmp_path: Path) -> None:
    result = audit_catalog(tmp_path / "missing")

    assert result.files == 0
    assert result.valid == 0
    assert result.invalid == 0
    assert result.issues == ()


def test_audit_counts_valid_and_invalid_records(tmp_path: Path) -> None:
    directory = tmp_path / "research"
    directory.mkdir()
    (directory / "valid.json").write_text(json.dumps(_document()), encoding="utf-8")
    invalid = _document()
    invalid["manifest"]["train_ratio"] = 0.8
    (directory / "invalid.json").write_text(json.dumps(invalid), encoding="utf-8")

    result = audit_catalog(directory)

    assert result.files == 2
    assert result.valid == 1
    assert result.invalid == 1
    assert len(result.issues) == 1
    assert "invalid.json" in result.issues[0]
