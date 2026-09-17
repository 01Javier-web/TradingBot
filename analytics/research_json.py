"""Serialización completa de una corrida de investigación."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai.research_pipeline import ResearchRun
from analytics.research_manifest import manifest_to_dict
from analytics.research_report import candidate_summary


def research_run_to_dict(run: ResearchRun) -> dict[str, Any]:
    """Convierte una corrida en un documento JSON estable y auditable."""
    return {
        "manifest": manifest_to_dict(run.manifest),
        "finding": {
            "experiments": run.finding.experiments,
            "profitable_train": run.finding.profitable_train,
            "profitable_test": run.finding.profitable_test,
            "generalization_rate": run.finding.generalization_rate,
            "findings": list(run.finding.findings),
        },
        "validation": {
            "valid": run.evidence.validation.valid,
            "issues": list(run.evidence.validation.issues),
        },
        "candidates": candidate_summary(run.evidence.candidates),
    }


def save_research_run(run: ResearchRun, path: str | Path) -> None:
    """Guarda la corrida completa sin modificar los resultados originales."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(research_run_to_dict(run), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
