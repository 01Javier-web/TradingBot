"""Metadatos de reproducibilidad para corridas de investigación."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from backtesting.optimizer import ParameterGrid


@dataclass(frozen=True)
class ResearchManifest:
    """Describe el contexto necesario para repetir una investigación."""

    rows: int
    train_ratio: float
    data_fingerprint: str
    fast_ema_periods: tuple[int, ...]
    slow_ema_periods: tuple[int, ...]
    rsi_periods: tuple[int, ...]

    @classmethod
    def from_grid(
        cls,
        rows: int,
        grid: ParameterGrid,
        train_ratio: float = 0.7,
        data_fingerprint: str = "",
    ) -> "ResearchManifest":
        if rows < 2:
            raise ValueError("rows debe ser al menos 2")
        if not 0 < train_ratio < 1:
            raise ValueError("train_ratio debe estar entre 0 y 1")
        if data_fingerprint and len(data_fingerprint) != 64:
            raise ValueError("data_fingerprint debe tener 64 caracteres SHA-256")
        if data_fingerprint and any(char not in "0123456789abcdef" for char in data_fingerprint.lower()):
            raise ValueError("data_fingerprint debe ser hexadecimal")
        return cls(
            rows=rows,
            train_ratio=train_ratio,
            data_fingerprint=data_fingerprint,
            fast_ema_periods=grid.fast_ema_periods,
            slow_ema_periods=grid.slow_ema_periods,
            rsi_periods=grid.rsi_periods,
        )


def manifest_to_dict(manifest: ResearchManifest) -> dict[str, Any]:
    """Convierte los metadatos a una estructura serializable."""
    return asdict(manifest)


def save_manifest(manifest: ResearchManifest, path: str | Path) -> None:
    """Guarda un manifiesto JSON sin incluir credenciales ni datos sensibles."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest_to_dict(manifest), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
