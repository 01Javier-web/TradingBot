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
        if not isinstance(self.results, tuple) or any(not isinstance(result, OptimizationResult) for result in self.results):
            raise ValueError("results debe ser una tupla de OptimizationResult")
        if not isinstance(self.finding, ResearchFinding):
            raise ValueError("finding debe ser ResearchFinding")
        if not isinstance(self.evidence, ResearchEvidence):
            raise ValueError("evidence debe ser ResearchEvidence")
        if not isinstance(self.manifest, ResearchManifest):
            raise ValueError("manifest debe ser ResearchManifest")
        if not isinstance(self.experiment_id, str) or len(self.experiment_id) != 64:
            raise ValueError("experiment_id debe ser SHA-256 hexadecimal")
        if any(char not in "0123456789abcdef" for char in self.experiment_id.lower()):
            raise ValueError("experiment_id debe ser hexadecimal")
        if self.experiment_id != build_experiment_id(self.manifest):
            raise ValueError("experiment_id no corresponde al manifiesto")
        if self.finding.experiments != len(self.results):
            raise ValueError("finding.experiments no coincide con results")
        # La evidencia puede representar deliberadamente una corrida inválida;
        # el gate de decisión debe poder auditarla y exigir revisión humana.
        # Un ResearchRun producido por run_research será válido; se permite
        # conservar evidencia inválida para que el gate de revisión humana
        # pueda representar y auditar una investigación problemática.


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
