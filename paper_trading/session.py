"""Orquestación completa de una sesión de paper trading."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from analytics.paper_audit import PaperAuditResult, audit_paper_events
from analytics.paper_report import PaperPerformanceReport
from data.quality import validate_time_series
from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from strategy.signals import StrategyConfig, generate_signals


@dataclass(frozen=True)
class PaperSessionResult:
    """Resultado auditable de una ejecución completa en simulación."""

    rows: int
    events: tuple[dict[str, object], ...]
    report: PaperPerformanceReport
    audit: PaperAuditResult
    mode: str = "simulation-first"
    execution_authorized: bool = False


class PaperTradingSession:
    """Une validación, indicadores, señales, motor de riesgo y reporte.

    Esta capa no tiene adaptador de ejecución y no puede enviar órdenes reales.
    Una instancia representa una sola sesión para evitar mezclar historiales.
    """

    def __init__(
        self,
        portfolio: PaperPortfolio,
        config: StrategyConfig | None = None,
        engine: PaperTradingEngine | None = None,
    ) -> None:
        self.portfolio = portfolio
        self.config = config or StrategyConfig()
        self.engine = engine or PaperTradingEngine(portfolio)
        if self.engine.portfolio is not portfolio:
            raise ValueError("El engine debe usar el mismo portfolio de la sesión")
        self._executed = False

    def run(self, df: pd.DataFrame) -> PaperSessionResult:
        """Procesa un DataFrame validado de principio a fin en modo paper."""
        if self._executed:
            raise RuntimeError("sesión ya ejecutada")

        data = validate_time_series(df)
        enriched = generate_signals(data, self.config)
        for _, row in enriched.iterrows():
            self.engine.process(row)

        self._executed = True
        report = self.engine.performance_report()
        audit = audit_paper_events(self.engine.history)
        return PaperSessionResult(
            rows=len(enriched),
            events=tuple(dict(event) for event in self.engine.history),
            report=report,
            audit=audit,
        )


__all__ = ["PaperSessionResult", "PaperTradingSession"]
