"""Pruebas de comparación de contexto entre experimentos."""

from analytics.research_compare import compare_context
from analytics.research_registry import ResearchRecord


def _record(
    *,
    fingerprint: str = "a" * 64,
    train_ratio: float = 0.7,
    fast: tuple[int, ...] = (5, 10),
    slow: tuple[int, ...] = (20, 30),
    rsi: tuple[int, ...] = (14,),
) -> ResearchRecord:
    return ResearchRecord(
        experiment_id="e1",
        data_fingerprint=fingerprint,
        rows=100,
        train_ratio=train_ratio,
        fast_ema_periods=fast,
        slow_ema_periods=slow,
        rsi_periods=rsi,
    )


def test_compare_context_detects_identical_context() -> None:
    comparison = compare_context(_record(), _record())

    assert comparison.same_context is True


def test_compare_context_detects_data_difference() -> None:
    comparison = compare_context(_record(), _record(fingerprint="b" * 64))

    assert comparison.same_data is False
    assert comparison.same_context is False


def test_compare_context_detects_parameter_difference() -> None:
    comparison = compare_context(_record(), _record(fast=(5, 20)))

    assert comparison.same_fast_ema_grid is False
    assert comparison.same_context is False


def test_compare_context_keeps_other_dimensions_explicit() -> None:
    comparison = compare_context(_record(), _record(train_ratio=0.8, slow=(25, 30), rsi=(21,)))

    assert comparison.same_data is True
    assert comparison.same_rows is True
    assert comparison.same_train_ratio is False
    assert comparison.same_fast_ema_grid is True
    assert comparison.same_slow_ema_grid is False
    assert comparison.same_rsi_grid is False
