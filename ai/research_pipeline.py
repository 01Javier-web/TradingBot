"""Pipeline reproducible para investigar estrategias en modo simulation-first.

Coordina la optimización, validación y resumen de resultados. Esta capa solo
produce evidencia de investigación: no cambia reglas de riesgo y no tiene
autoridad de ejecución.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ai.research_evidence import ResearchEvidence, build_evidence
from ai.researcher import ResearchFinding, summarize_optimization
from backtesting.optimizer import OptimizationResult, ParameterGrid, optimize


@dataclass(frozen=True)
class ResearchRun:
    """Resultado completo y auditable de una corrida de investigación."""

    results: tuple[OptimizationResult, ...]
    finding: ResearchFinding
    evidence: ResearchEvidence


def run_research(df: pd.DataFrame, grid: ParameterGrid) -> ResearchRun:
    """Ejecuta optimización y construye evidencia reproducible."""
    results = optimize(df, grid)
    finding = summarize_optimization(results)
    evidence = build_evidence(results)
    return ResearchRun(tuple(results), finding, evidence)
