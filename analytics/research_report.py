"""Formato auditable para resultados de investigación de estrategias."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from ai.researcher import ResearchFinding


def save_research_finding(finding: ResearchFinding, path: str | Path) -> None:
    """Guarda un hallazgo en JSON para reproducibilidad y auditoría."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(asdict(finding), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
