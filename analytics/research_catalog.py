"""Catálogo descriptivo de experimentos registrados."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from analytics.research_registry import ResearchRecord, list_research_records


def catalog_records(directory: str | Path) -> tuple[ResearchRecord, ...]:
    """Obtiene el catálogo ordenado de investigaciones disponibles."""
    return list_research_records(directory)


def catalog_to_dict(records: tuple[ResearchRecord, ...]) -> list[dict[str, Any]]:
    """Convierte referencias del catálogo en estructuras serializables."""
    return [asdict(record) for record in records]


def save_catalog(records: tuple[ResearchRecord, ...], path: str | Path) -> None:
    """Exporta un índice del catálogo sin incluir resultados sensibles."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(catalog_to_dict(records), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
