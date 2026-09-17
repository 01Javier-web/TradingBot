"""Gestor de riesgo para simulación y futura ejecución controlada."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from risk.validation import validate_risk_inputs


@dataclass(frozen=True)
class RiskConfig:
    """Límites que una señal debe cumplir antes de ser aprobada."""

    max_risk_per_trade: float = 0.01
    max_daily_loss: float = 0.02
    max_open_positions: int = 1
    stop_loss_required: bool = True

    def __post_init__(self) -> None:
        if not isfinite(self.max_risk_per_trade) or not 0 < self.max_risk_per_trade <= 1:
            raise ValueError("max_risk_per_trade debe ser finito y estar entre 0 y 1")
        if not isfinite(self.max_daily_loss) or not 0 < self.max_daily_loss <= 1:
            raise ValueError("max_daily_loss debe ser finito y estar entre 0 y 1")
        if self.max_open_positions <= 0:
            raise ValueError("max_open_positions debe ser mayor que 0")


@dataclass(frozen=True)
class RiskDecision:
    """Resultado auditable de la evaluación de riesgo."""

    approved: bool
    reason: str


class RiskManager:
    """Aplica límites duros antes de permitir una operación simulada."""

    def __init__(self, config: RiskConfig | None = None) -> None:
        self.config = config or RiskConfig()

    def approve(
        self,
        *,
        balance: float,
        risk_amount: float,
        daily_loss: float,
        open_positions: int,
        stop_loss_distance: float | None,
    ) -> RiskDecision:
        validation = validate_risk_inputs(
            balance=balance,
            risk_amount=risk_amount,
            daily_loss=daily_loss,
            open_positions=open_positions,
            stop_loss_distance=stop_loss_distance,
        )
        if not validation.valid:
            return RiskDecision(False, "entradas de riesgo inválidas: " + " ".join(validation.issues))

        if risk_amount > balance * self.config.max_risk_per_trade:
            return RiskDecision(False, "supera el riesgo máximo por operación")
        if daily_loss >= balance * self.config.max_daily_loss:
            return RiskDecision(False, "límite de pérdida diaria alcanzado")
        if open_positions >= self.config.max_open_positions:
            return RiskDecision(False, "máximo de posiciones abiertas alcanzado")
        if self.config.stop_loss_required and (stop_loss_distance is None or stop_loss_distance <= 0):
            return RiskDecision(False, "stop-loss obligatorio ausente o inválido")
        return RiskDecision(True, "operación aprobada por Risk Manager")


__all__ = ["RiskConfig", "RiskDecision", "RiskManager"]
