"""Pruebas del CLI del catálogo de investigación."""

from analytics.research_registry import ResearchRecord
from app.research_catalog_cli import format_catalog


def test_format_catalog_has_stable_context_fields() -> None:
    record = ResearchRecord(
        experiment_id="abc123",
        data_fingerprint="a" * 64,
        rows=80,
        train_ratio=0.7,
        fast_ema_periods=(5, 10),
        slow_ema_periods=(20, 30),
        rsi_periods=(14,),
    )

    output = format_catalog((record,))

    assert "Investigaciones: 1" in output
    assert "ID: abc123" in output
    assert "Filas: 80" in output
    assert "Train ratio: 0.7" in output
    assert "EMA rápidas: (5, 10)" in output
    assert "Modo: simulation-first" in output


def test_format_empty_catalog() -> None:
    output = format_catalog(())

    assert output.startswith("=== TradingBot Research Catalog ===")
    assert "Investigaciones: 0" in output
    assert "Modo: simulation-first" in output
