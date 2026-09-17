"""Formato de texto estable para corridas de investigación."""

from __future__ import annotations

from ai.research_pipeline import ResearchRun
from ai.research_quality import assess_quality


def format_research_run(run: ResearchRun) -> str:
    """Genera un resumen humano y reproducible sin ordenar por rentabilidad."""
    quality = assess_quality(list(run.results))
    lines = [
        "=== TradingBot Research Report ===",
        f"Resultados: {len(run.results)}",
        f"Validación: {'OK' if run.evidence.validation.valid else 'ERROR'}",
        f"Calidad - muestras: {quality.sample_size}",
        f"Calidad - resultados finitos: {'SI' if quality.finite_results else 'NO'}",
        f"Calidad - generalización train+test: {quality.generalization_rate:.1%}",
    ]

    if run.evidence.validation.issues:
        lines.append("Problemas:")
        lines.extend(f"- {issue}" for issue in run.evidence.validation.issues)

    lines.extend(
        [
            f"Candidatos consistentes: {sum(item.consistent for item in run.evidence.candidates)}",
            *run.finding.findings,
            "Modo: simulation-first",
            "Ejecución real: BLOQUEADA",
        ]
    )
    return "\n".join(lines)
