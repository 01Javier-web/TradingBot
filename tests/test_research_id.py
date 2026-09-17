"""Pruebas del identificador reproducible de experimentos."""

from analytics.research_id import build_experiment_id
from analytics.research_manifest import ResearchManifest
from backtesting.optimizer import ParameterGrid


def _manifest() -> ResearchManifest:
    return ResearchManifest.from_grid(
        80,
        ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)),
        train_ratio=0.7,
        data_fingerprint="a" * 64,
    )


def test_same_manifest_produces_same_experiment_id() -> None:
    assert build_experiment_id(_manifest()) == build_experiment_id(_manifest())


def test_different_data_fingerprint_changes_experiment_id() -> None:
    first = _manifest()
    second = ResearchManifest.from_grid(
        80,
        ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)),
        data_fingerprint="b" * 64,
    )

    assert build_experiment_id(first) != build_experiment_id(second)


def test_experiment_id_is_sha256_hex() -> None:
    experiment_id = build_experiment_id(_manifest())

    assert len(experiment_id) == 64
    assert all(character in "0123456789abcdef" for character in experiment_id)
