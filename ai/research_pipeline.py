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
from ai.research_validation import validate_results
from analytics.research_fingerprint import fingerprint_dataframe
from analytics.research_id import build_experiment_id
from analytics.research_manifest import ResearchManifest
from backtesting.optimizer import OptimizationResult, ParameterGrid, optimize


@dataclass(frozen=True)
class ResearchRun:
    """Resultado completo y auditable de una corrida de investigación."""

    results: tuple[OptimizationResult, ...]
    finding: ResearchFinding
    evidence: ResearchEvidence
    manifest: ResearchManifest
    experiment_id: str

    def __post_init__(self) -> None:
        if not self.experiment_id or len(self.experiment_id) != 64:
            raise ValueError("experiment_id debe ser SHA-256 hexadecimal")
        if any(char not in "0123456789abcdef" for char in self.experiment_id.lower()):
            raise ValueError("experiment_id debe ser hexadecimal")


def run_research(
    df: pd.DataFrame,
    grid: ParameterGrid,
    train_ratio: float = 0.7,
) -> ResearchRun:
    """Ejecuta optimización y conserva el contexto usado para repetirla."""
    data_fingerprint = fingerprint_dataframe(df)
    results = optimize(df, grid, train_ratio=train_ratio)
    validation = validate_results(results)
    if not validation.valid:
        raise ValueError("Resultados de investigación inválidos: " + " ".join(validation.issues))

    finding = summarize_optimization(results)
    evidence = build_evidence(results)
    manifest = ResearchManifest.from_grid(
        len(df),
        grid,
        train_ratio=train_ratio,
        data_fingerprint=data_fingerprint,
    )
    experiment_id = build_experiment_id(manifest)
    return ResearchRun(tuple(results), finding, evidence, manifest, experiment_id)
