"""Resumen descriptivo de investigaciones registradas."""

from __future__ import annotations

from dataclasses import dataclass

from analytics.research_registry import ResearchRecord


@dataclass(frozen=True)
class ResearchSummary:
    """Conteo y contexto común de un conjunto de investigaciones."""

    total: int
    unique_data_fingerprints: int
    unique_train_ratios: int
    unique_parameter_grids: int


def summarize_records(records: tuple[ResearchRecord, ...]) -> ResearchSummary:
    """Resume diversidad de contexto sin ordenar ni valorar rendimiento."""
    grids = {
        (
            record.fast_ema_periods,
            record.slow_ema_periods,
            record.rsi_periods,
        )
        for record in records
    }
    return ResearchSummary(
        total=len(records),
        unique_data_fingerprints=len({record.data_fingerprint for record in records}),
        unique_train_ratios=len({record.train_ratio for record in records}),
        unique_parameter_grids=len(grids),
    )
