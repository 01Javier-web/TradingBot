"""Formato auditable para resultados de investigación de estrategias."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from ai.researcher import ResearchFinding
from ai.research_selection import ResearchCandidate


def save_research_finding(finding: ResearchFinding, path: str | Path) -> None:
    """Guarda un hallazgo en JSON para reproducibilidad y auditoría."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(asdict(finding), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def candidate_summary(candidates: tuple[ResearchCandidate, ...]) -> list[dict[str, object]]:
    """Convierte candidatos en una vista serializable para reportes."""
    return [
        {
            "fast_ema_period": candidate.result.config.fast_ema_period,
            "slow_ema_period": candidate.result.config.slow_ema_period,
            "rsi_period": candidate.result.config.rsi_period,
            "train_pnl": candidate.result.train_pnl,
            "test_pnl": candidate.result.test_pnl,
            "consistent": candidate.consistent,
        }
        for candidate in candidates
    ]
