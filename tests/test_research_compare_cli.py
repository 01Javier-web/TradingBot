"""Pruebas del CLI de comparación de investigaciones."""

import pytest

from analytics.research_compare import compare_context
from analytics.research_registry import ResearchRecord
from app.research_compare_cli import find_record, format_comparison


def _record(experiment_id: str, *, fast=(5, 10)) -> ResearchRecord:
    return ResearchRecord(
        experiment_id=experiment_id,
        data_fingerprint="a" * 64,
        rows=100,
        train_ratio=0.7,
        fast_ema_periods=fast,
        slow_ema_periods=(20, 30),
        rsi_periods=(14,),
    )


def test_find_record_returns_requested_experiment() -> None:
    first = _record("one")
    second = _record("two")

    assert find_record((first, second), "two") == second


def test_find_record_rejects_unknown_experiment() -> None:
    with pytest.raises(ValueError, match="missing"):
        find_record((_record("one"),), "missing")


def test_format_comparison_exposes_context_without_ranking() -> None:
    first = _record("one")
    second = _record("two", fast=(5, 20))
    comparison = compare_context(first, second)

    output = format_comparison(first, second, comparison)

    assert "Mismos datos: SI" in output
    assert "Mismo grid EMA rápidas: NO" in output
    assert "Mismo contexto: NO" in output
    assert "selecciona una estrategia" in output
