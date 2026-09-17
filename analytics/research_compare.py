"""Comparación descriptiva de investigaciones registradas."""

from __future__ import annotations

from dataclasses import dataclass

from analytics.research_registry import ResearchRecord


@dataclass(frozen=True)
class ResearchComparison:
    """Diferencias de contexto entre dos experimentos."""

    same_data: bool
    same_rows: bool
    same_train_ratio: bool
    same_fast_ema_grid: bool
    same_slow_ema_grid: bool
    same_rsi_grid: bool

    @property
    def same_context(self) -> bool:
        """Indica si ambos experimentos usaron exactamente el mismo contexto."""
        return all(
            (
                self.same_data,
                self.same_rows,
                self.same_train_ratio,
                self.same_fast_ema_grid,
                self.same_slow_ema_grid,
                self.same_rsi_grid,
            )
        )


def compare_context(first: ResearchRecord, second: ResearchRecord) -> ResearchComparison:
    """Compara el contexto sin comparar ni seleccionar resultados de rendimiento."""
    return ResearchComparison(
        same_data=first.data_fingerprint == second.data_fingerprint,
        same_rows=first.rows == second.rows,
        same_train_ratio=first.train_ratio == second.train_ratio,
        same_fast_ema_grid=first.fast_ema_periods == second.fast_ema_periods,
        same_slow_ema_grid=first.slow_ema_periods == second.slow_ema_periods,
        same_rsi_grid=first.rsi_periods == second.rsi_periods,
    )
