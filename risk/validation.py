"""Validación estructural de entradas para el gestor de riesgo."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class RiskInputValidation:
    """Resultado de validar los datos recibidos por la capa de riesgo."""

    valid: bool
    issues: tuple[str, ...]


def validate_risk_inputs(
    *,
    balance: float,
    risk_amount: float,
    daily_loss: float,
    open_positions: int,
    stop_loss_distance: float | None,
) -> RiskInputValidation:
    """Detecta valores no finitos o inconsistentes antes de evaluar límites."""
    issues: list[str] = []

    numeric_values = {
        "balance": balance,
        "risk_amount": risk_amount,
        "daily_loss": daily_loss,
    }
    for name, value in numeric_values.items():
        if not isfinite(value):
            issues.append(f"{name} debe ser finito.")

    if balance <= 0:
        issues.append("balance debe ser mayor que 0.")
    if risk_amount <= 0:
        issues.append("risk_amount debe ser mayor que 0.")
    if daily_loss < 0:
        issues.append("daily_loss no puede ser negativo.")
    if open_positions < 0:
        issues.append("open_positions no puede ser negativo.")
    if stop_loss_distance is not None:
        if not isfinite(stop_loss_distance):
            issues.append("stop_loss_distance debe ser finito.")
        elif stop_loss_distance <= 0:
            issues.append("stop_loss_distance debe ser mayor que 0.")

    return RiskInputValidation(valid=not issues, issues=tuple(issues))
