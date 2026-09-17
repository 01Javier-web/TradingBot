"""Coordinador mínimo de agentes de análisis.

El coordinador organiza observaciones; no puede ejecutar operaciones ni
modificar los límites del Risk Manager.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ai.market_analyst import MarketAnalysis, analyze_row


@dataclass(frozen=True)
class AnalysisReport:
    """Reporte agregado producido por agentes observadores."""

    market: MarketAnalysis
    recommendation: str


class Coordinator:
    """Orquesta análisis sin otorgar permisos de ejecución a los agentes."""

    def analyze(self, row: pd.Series) -> AnalysisReport:
        market = analyze_row(row)
        if market.signal.value == "WAIT":
            recommendation = "WAIT"
        else:
            recommendation = market.signal.value
        return AnalysisReport(market=market, recommendation=recommendation)
