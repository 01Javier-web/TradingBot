"""Validaciones estructurales para resultados walk-forward."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backtesting.walk_forward import WalkForwardWindow


@dataclass(frozen=True)
class WalkForwardValidation:
    """Estado de calidad de una ejecución walk-forward."""

    valid: bool
    windows: int
    issues: tuple[str, ...]


def validate_walk_forward(windows: tuple["WalkForwardWindow", ...]) -> WalkForwardValidation:
    """Comprueba orden temporal, ventanas no vacías y PnL finito."""
    issues: list[str] = []

    for index, window in enumerate(windows, start=1):
        if window.train_start >= window.train_end:
            issues.append(f"Ventana {index}: train debe contener al menos dos instantes ordenados.")
        if window.test_start >= window.test_end:
            issues.append(f"Ventana {index}: test debe contener al menos dos instantes ordenados.")
        if window.train_end >= window.test_start:
            issues.append(f"Ventana {index}: train y test se solapan o no respetan el orden temporal.")
        if not isfinite(float(window.test_pnl)):
            issues.append(f"Ventana {index}: test_pnl no es finito.")

    for previous, current in zip(windows, windows[1:]):
        if current.train_start <= previous.train_start:
            issues.append("Los inicios de train deben avanzar estrictamente.")
        if current.test_start <= previous.test_start:
            issues.append("Los inicios de test deben avanzar estrictamente.")

    return WalkForwardValidation(
        valid=not issues,
        windows=len(windows),
        issues=tuple(issues),
    )
