"""Kill switch local para detener la simulación ante condiciones críticas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KillSwitch:
    """Estado de parada explícita y auditable."""

    active: bool = False
    reason: str | None = None

    def trigger(self, reason: str) -> None:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("El motivo del kill switch debe ser texto no vacío")
        self.active = True
        self.reason = reason.strip()

    def reset(self) -> None:
        self.active = False
        self.reason = None

    def check(self) -> None:
        if self.active:
            raise RuntimeError(f"Kill switch activo: {self.reason}")
