"""Ciclo seguro de datos de mercado hacia paper trading."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data.quality import validate_time_series
from paper_trading.session import PaperSessionResult, PaperTradingSession


@dataclass(frozen=True)
class PaperCycleResult:
    """Resultado del ciclo de procesamiento de mercado en simulación."""

    session: PaperSessionResult
    rows_processed: int
    mode: str = "simulation-first"
    execution_authorized: bool = False


def run_paper_cycle(df: pd.DataFrame, session: PaperTradingSession) -> PaperCycleResult:
    """Valida y procesa un lote completo de velas sin ninguna ejecución real."""
    data = validate_time_series(df)
    result = session.run(data)
    return PaperCycleResult(
        session=result,
        rows_processed=len(data),
    )


__all__ = ["PaperCycleResult", "run_paper_cycle"]
