"""Validación estructural de trazabilidad de sesiones de paper trading."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


_REQUIRED = {"sequence", "action"}


@dataclass(frozen=True)
class PaperAuditResult:
    """Resultado de una auditoría estructural de eventos."""

    valid: bool
    event_count: int
    issues: tuple[str, ...]


def audit_paper_events(events: Iterable[dict[str, object]]) -> PaperAuditResult:
    """Comprueba secuencia, acciones y campos numéricos sin alterar eventos."""
    issues: list[str] = []
    count = 0
    previous_sequence = 0
    allowed_actions = {"OPEN", "CLOSE", "STOP_LOSS", "REJECTED", "KILL_SWITCH"}

    for count, event in enumerate(events, start=1):
        missing = _REQUIRED - set(event)
        if missing:
            issues.append(f"evento {count}: faltan campos {sorted(missing)}")
            continue

        sequence = event.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence != previous_sequence + 1:
            issues.append(f"evento {count}: secuencia no monotónica")
        previous_sequence = sequence if isinstance(sequence, int) and not isinstance(sequence, bool) else previous_sequence

        action = event.get("action")
        if action not in allowed_actions:
            issues.append(f"evento {count}: acción no permitida")

        for field in ("price", "quantity", "stop_loss", "pnl"):
            value = event.get(field)
            if value is not None:
                try:
                    numeric = float(value)
                except (TypeError, ValueError):
                    issues.append(f"evento {count}: {field} no numérico")
                    continue
                if not isfinite(numeric):
                    issues.append(f"evento {count}: {field} no finito")

    return PaperAuditResult(
        valid=not issues,
        event_count=count,
        issues=tuple(issues),
    )


__all__ = ["PaperAuditResult", "audit_paper_events"]
