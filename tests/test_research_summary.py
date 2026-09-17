"""Pruebas del resumen de investigaciones."""

from analytics.research_registry import ResearchRecord
from analytics.research_summary import summarize_records


def _record(experiment_id: str, fingerprint: str, train_ratio: float, fast=(5, 10)) -> ResearchRecord:
    return ResearchRecord(
        experiment_id=experiment_id,
        data_fingerprint=fingerprint,
        rows=100,
        train_ratio=train_ratio,
        fast_ema_periods=fast,
        slow_ema_periods=(20, 30),
        rsi_periods=(14,),
    )


def test_summary_counts_context_dimensions() -> None:
    records = (
        _record("a", "a" * 64, 0.7),
        _record("b", "a" * 64, 0.7, fast=(5, 20)),
        _record("c", "b" * 64, 0.8),
    )

    summary = summarize_records(records)

    assert summary.total == 3
    assert summary.unique_data_fingerprints == 2
    assert summary.unique_train_ratios == 2
    assert summary.unique_parameter_grids == 2


def test_summary_of_empty_catalog_is_zero() -> None:
    summary = summarize_records(())

    assert summary.total == 0
    assert summary.unique_data_fingerprints == 0
    assert summary.unique_train_ratios == 0
    assert summary.unique_parameter_grids == 0
