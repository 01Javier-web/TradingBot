"""Pruebas de integridad de investigaciones almacenadas."""

from analytics.research_integrity import validate_record_integrity


def _document() -> dict:
    from analytics.research_manifest import ResearchManifest
    from analytics.research_id import build_experiment_id

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


def test_integrity_accepts_matching_manifest_and_id() -> None:
    result = validate_record_integrity(_document())

    assert result.valid is True
    assert result.issues == ()


def test_integrity_rejects_changed_manifest() -> None:
    document = _document()
    document["manifest"]["train_ratio"] = 0.8

    result = validate_record_integrity(document)

    assert result.valid is False
    assert "experiment_id" in result.issues[0]


def test_integrity_rejects_missing_manifest() -> None:
    result = validate_record_integrity({"experiment_id": "abc"})

    assert result.valid is False
    assert "manifiesto" in result.issues[0]
