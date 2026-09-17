"""Caso de uso de simulación: analiza señales y las pasa por el Risk Manager."""

from __future__ import annotations

import pandas as pd

from ai.coordinator import AnalysisReport, Coordinator
from paper_trading.engine import PaperTradingEngine
from paper_trading.runner import run_dataframe


class SimulationService:
    """Punto de entrada de alto nivel para pruebas sin broker real."""

    def __init__(self, engine: PaperTradingEngine, coordinator: Coordinator | None = None) -> None:
        self.engine = engine
        self.coordinator = coordinator or Coordinator()

    def analyze(self, row: pd.Series) -> AnalysisReport:
        return self.coordinator.analyze(row)

    def run(self, df: pd.DataFrame) -> list[str]:
        """Procesa datos históricos en modo paper trading exclusivamente."""
        return run_dataframe(df, self.engine)
