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
    fast_ema_periods: tuple[int, ...]
    slow_ema_periods: tuple[int, ...]
    rsi_periods: tuple[int, ...]


def record_from_run(run: ResearchRun) -> ResearchRecord:
    """Extrae una referencia estable de una corrida."""
    return ResearchRecord(
        experiment_id=run.experiment_id,
        data_fingerprint=run.manifest.data_fingerprint,
        rows=run.manifest.rows,
        train_ratio=run.manifest.train_ratio,
        fast_ema_periods=run.manifest.fast_ema_periods,
        slow_ema_periods=run.manifest.slow_ema_periods,
        rsi_periods=run.manifest.rsi_periods,
    )


def save_research_record(
    run: ResearchRun,
    directory: str | Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Guarda una corrida identificada por su ID, evitando sobrescrituras accidentales."""
    destination = Path(directory)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / f"{run.experiment_id}.json"
    content = json.dumps(research_run_to_dict(run), indent=2, ensure_ascii=False)

    if path.exists() and not overwrite:
        existing = path.read_text(encoding="utf-8")
        if existing != content:
            raise FileExistsError(
                f"Ya existe una investigación diferente con el ID {run.experiment_id}"
            )
        return path

    path.write_text(content, encoding="utf-8")
    return path


def load_research_record(path: str | Path) -> dict[str, Any]:
    """Carga una corrida previamente registrada."""
    source = Path(path)
    return json.loads(source.read_text(encoding="utf-8"))


def list_research_records(directory: str | Path) -> tuple[ResearchRecord, ...]:
    """Lista investigaciones registradas ordenadas por ID, sin ejecutar nada."""
    destination = Path(directory)
    if not destination.exists():
        return ()

    records: list[ResearchRecord] = []
    for path in sorted(destination.glob("*.json")):
        document = load_research_record(path)
        manifest = document["manifest"]
        records.append(
            ResearchRecord(
                experiment_id=document["experiment_id"],
                data_fingerprint=manifest["data_fingerprint"],
                rows=manifest["rows"],
                train_ratio=manifest["train_ratio"],
                fast_ema_periods=tuple(manifest["fast_ema_periods"]),
                slow_ema_periods=tuple(manifest["slow_ema_periods"]),
                rsi_periods=tuple(manifest["rsi_periods"]),
            )
        )
    return tuple(records)


def compare_research_records(
    first: ResearchRecord,
    second: ResearchRecord,
) -> dict[str, object]:
    """Describe diferencias de datos, partición y parámetros entre investigaciones."""
    return {
        "same_data": first.data_fingerprint == second.data_fingerprint,
        "same_rows": first.rows == second.rows,
        "same_train_ratio": first.train_ratio == second.train_ratio,
        "same_fast_ema_grid": first.fast_ema_periods == second.fast_ema_periods,
        "same_slow_ema_grid": first.slow_ema_periods == second.slow_ema_periods,
        "same_rsi_grid": first.rsi_periods == second.rsi_periods,
        "first_experiment_id": first.experiment_id,
        "second_experiment_id": second.experiment_id,
    }
