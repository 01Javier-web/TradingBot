"""Validación estructural de trazabilidad de sesiones de paper trading."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

import pandas as pd


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
    previous_time = None
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

        market_time = event.get("market_time")
        if market_time is not None:
            try:
                current_time = pd.Timestamp(market_time)
                if current_time.tzinfo is None:
                    current_time = current_time.tz_localize("UTC")
                else:
                    current_time = current_time.tz_convert("UTC")
                if previous_time is not None and current_time < previous_time:
                    issues.append(f"evento {count}: market_time retrocede")
                previous_time = current_time
            except (TypeError, ValueError):
                issues.append("market_time inválido")

        action = event.get("action")
        if action not in allowed_actions:
            issues.append(f"evento {count}: acción no permitida")

        required_by_action = {
            "OPEN": ("side", "price", "quantity", "stop_loss"),
            "CLOSE": ("side", "price", "quantity", "pnl"),
            "STOP_LOSS": ("side", "price", "quantity", "pnl"),
            "REJECTED": ("reason",),
            "KILL_SWITCH": ("reason",),
        }
        if action in required_by_action:
            for field in required_by_action[action]:
                if event.get(field) is None:
                    issues.append(f"{action} requiere {field}")

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
