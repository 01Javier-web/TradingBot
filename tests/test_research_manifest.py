"""Pruebas del manifiesto de reproducibilidad."""

from pathlib import Path

import pytest

from analytics.research_manifest import ResearchManifest, manifest_to_dict, save_manifest
from backtesting.optimizer import ParameterGrid


def test_manifest_records_grid_and_dataset_size() -> None:
    grid = ParameterGrid(fast_ema_periods=(5, 10), slow_ema_periods=(20,), rsi_periods=(14, 21))

    manifest = ResearchManifest.from_grid(160, grid, train_ratio=0.75)

    assert manifest.rows == 160
    assert manifest.train_ratio == 0.75
    assert manifest.fast_ema_periods == (5, 10)
    assert manifest.slow_ema_periods == (20,)
    assert manifest.rsi_periods == (14, 21)


def test_manifest_serializes_without_credentials() -> None:
    manifest = ResearchManifest.from_grid(80, ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,)))

    document = manifest_to_dict(manifest)

    assert document["rows"] == 80
    assert "MT5_LOGIN" not in document
    assert "password" not in document


def test_manifest_can_be_saved(tmp_path: Path) -> None:
    manifest = ResearchManifest.from_grid(80, ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,)))
    destination = tmp_path / "research" / "manifest.json"

    save_manifest(manifest, destination)

    assert destination.exists()
    assert '"train_ratio": 0.7' in destination.read_text(encoding="utf-8")


def test_manifest_rejects_invalid_inputs() -> None:
    grid = ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,))

    with pytest.raises(ValueError, match="rows"):
        ResearchManifest.from_grid(1, grid)

    with pytest.raises(ValueError, match="train_ratio"):
        ResearchManifest.from_grid(80, grid, train_ratio=1.0)
