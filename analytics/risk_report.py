"""Reporte auditable de una evaluación de riesgo."""

from __future__ import annotations

from typing import Any

from risk.manager import RiskDecision
from risk.validation import RiskInputValidation


def risk_decision_to_dict(
    decision: RiskDecision,
    validation: RiskInputValidation | None = None,
) -> dict[str, Any]:
    """Serializa validación y decisión sin introducir autoridad de ejecución."""
    return {
        "input_validation": (
            {
                "valid": validation.valid,
                "issues": list(validation.issues),
            }
            if validation is not None
            else None
        ),
        "approved": decision.approved,
        "reason": decision.reason,
        "execution_authorized": False,
        "mode": "simulation-first",
    }
