"""Pipeline reproducible para investigar estrategias en modo simulation-first.

Coordina la generación de configuraciones, el backtesting de cada variante y
el resumen train/test. Esta capa solo produce evidencia de investigación:
no cambia reglas de riesgo y no tiene autoridad de ejecución.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ai.researcher import ResearchFinding, summarize_optimization
from backtesting.optimizer import OptimizationResult, ParameterGrid, optimize


@dataclass(frozen=True)
class ResearchRun:
    """Resultado completo y auditable de una corrida de investigación."""

    results: tuple[OptimizationResult, ...]
    finding: ResearchFinding


def run_research(
    df: pd.DataFrame,
    grid: ParameterGrid,
) -> ResearchRun:
    """Ejecuta optimización y resume su capacidad de generalización.

    La función delega el cálculo cuantitativo al optimizador existente y no
    selecciona una configuración para operar automáticamente.
    """
    results = optimize(df, grid)
    finding = summarize_optimization(results)
    return ResearchRun(tuple(results), finding)
