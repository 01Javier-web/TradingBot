"""Kill switch local para detener la simulación ante condiciones críticas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KillSwitch:
    """Estado de parada explícita y auditable."""

    active: bool = False
    reason: str | None = None

    def trigger(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("El motivo del kill switch no puede estar vacío")
        self.active = True
        self.reason = reason

    def reset(self) -> None:
        self.active = False
        self.reason = None

    def check(self) -> None:
        """Lanza una excepción si la ejecución debe detenerse."""
        if self.active:
            raise RuntimeError(f"Kill switch activo: {self.reason}")
