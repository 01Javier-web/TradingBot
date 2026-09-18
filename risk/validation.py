"""Validación estructural de entradas para el gestor de riesgo."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real


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
        if isinstance(value, bool) or not isinstance(value, Real):
            issues.append(f"{name} debe ser numérico.")
        elif not isfinite(float(value)):
            issues.append(f"{name} debe ser finito.")

    if isinstance(balance, Real) and not isinstance(balance, bool) and balance <= 0:
        issues.append("balance debe ser mayor que 0.")
    if isinstance(risk_amount, Real) and not isinstance(risk_amount, bool) and risk_amount <= 0:
        issues.append("risk_amount debe ser mayor que 0.")
    if isinstance(daily_loss, Real) and not isinstance(daily_loss, bool) and daily_loss < 0:
        issues.append("daily_loss no puede ser negativo.")
    if isinstance(open_positions, bool) or not isinstance(open_positions, int):
        issues.append("open_positions debe ser un entero.")
    elif open_positions < 0:
        issues.append("open_positions no puede ser negativo.")
    if stop_loss_distance is not None:
        if isinstance(stop_loss_distance, bool) or not isinstance(stop_loss_distance, Real):
            issues.append("stop_loss_distance debe ser numérico.")
        elif not isfinite(float(stop_loss_distance)):
            issues.append("stop_loss_distance debe ser finito.")
        elif stop_loss_distance <= 0:
            issues.append("stop_loss_distance debe ser mayor que 0.")

    return RiskInputValidation(valid=not issues, issues=tuple(issues))
