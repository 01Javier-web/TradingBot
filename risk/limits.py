"""Evaluación de límites de riesgo independiente de la estrategia."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class RiskLimits:
    """Límites absolutos usados para bloquear una operación."""

    max_risk_per_trade: float = 0.01
    max_daily_loss: float = 0.02
    max_open_positions: int = 1

    def __post_init__(self) -> None:
        if not isfinite(self.max_risk_per_trade) or not 0 < self.max_risk_per_trade <= 1:
            raise ValueError("max_risk_per_trade debe ser finito y estar entre 0 y 1")
        if not isfinite(self.max_daily_loss) or not 0 < self.max_daily_loss <= 1:
            raise ValueError("max_daily_loss debe ser finito y estar entre 0 y 1")
        if self.max_open_positions <= 0:
            raise ValueError("max_open_positions debe ser mayor que 0")


def risk_budget(balance: float, limits: RiskLimits) -> float:
    """Calcula el importe máximo de riesgo permitido por operación."""
    if not isfinite(balance) or balance <= 0:
        raise ValueError("balance debe ser finito y mayor que 0")
    return balance * limits.max_risk_per_trade
