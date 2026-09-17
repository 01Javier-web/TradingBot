"""Registro local de corridas de investigación reproducibles."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from ai.research_pipeline import ResearchRun
from analytics.research_json import research_run_to_dict


@dataclass(frozen=True)
class ResearchRecord:
    """Referencia mínima de una investigación almacenada."""

    experiment_id: str
    data_fingerprint: str
    rows: int
    train_ratio: float


def record_from_run(run: ResearchRun) -> ResearchRecord:
    """Extrae una referencia estable de una corrida."""
    return ResearchRecord(
        experiment_id=run.experiment_id,
        data_fingerprint=run.manifest.data_fingerprint,
        rows=run.manifest.rows,
        train_ratio=run.manifest.train_ratio,
    )


def save_research_record(run: ResearchRun, directory: str | Path) -> Path:
    """Guarda una corrida usando su ID como nombre, sin sobrescribir otra."""
    destination = Path(directory)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"{run.experiment_id}.json"
    path.write_text(
        json.dumps(research_run_to_dict(run), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def load_research_record(path: str | Path) -> dict[str, Any]:
    """Carga una corrida previamente registrada."""
    source = Path(path)
    return json.loads(source.read_text(encoding="utf-8"))
