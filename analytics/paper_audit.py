"""Validación estructural de trazabilidad de sesiones de paper trading."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

import pandas as pd


_REQUIRED = {"sequence", "action"}
_ALLOWED_ACTIONS = {"OPEN", "CLOSE", "STOP_LOSS", "REJECTED", "KILL_SWITCH"}
_ALLOWED_SIDES = {"BUY", "SELL"}
_REQUIRED_BY_ACTION = {
    "OPEN": ("side", "price", "quantity", "stop_loss"),
    "CLOSE": ("side", "price", "quantity", "pnl"),
    "STOP_LOSS": ("side", "price", "quantity", "pnl"),
    "REJECTED": ("reason",),
    "KILL_SWITCH": ("reason",),
}


@dataclass(frozen=True)
class PaperAuditResult:
    """Resultado de una auditoría estructural de eventos."""

    valid: bool
    event_count: int
    issues: tuple[str, ...]


def audit_paper_events(events: Iterable[dict[str, object]]) -> PaperAuditResult:
    """Comprueba secuencia, esquema, tiempos y valores numéricos."""
    issues: list[str] = []
    count = 0
    previous_sequence = 0
    previous_time = None
    open_side = None

    for count, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            issues.append(f"evento {count}: debe ser un objeto")
            continue

        missing = _REQUIRED - set(event)
        if missing:
            issues.append(f"evento {count}: faltan campos {sorted(missing)}")
            continue

        sequence = event.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence != previous_sequence + 1:
            issues.append(f"evento {count}: secuencia no monotónica")
        if isinstance(sequence, int) and not isinstance(sequence, bool):
            previous_sequence = sequence

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
        if action not in _ALLOWED_ACTIONS:
            issues.append(f"evento {count}: acción no permitida")
            continue

        for field in _REQUIRED_BY_ACTION[action]:
            if event.get(field) is None:
                issues.append(f"{action} requiere {field}")

        if action in {"OPEN", "CLOSE", "STOP_LOSS"}:
            side = event.get("side")
            if side is not None and side not in _ALLOWED_SIDES:
                issues.append(f"{action} side inválido")

        for field in ("price", "quantity", "stop_loss", "pnl"):
            value = event.get(field)
            if value is None:
                continue
            if isinstance(value, bool):
                issues.append(f"evento {count}: {field} no numérico")
                continue
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                issues.append(f"evento {count}: {field} no numérico")
                continue
            if not isfinite(numeric):
                issues.append(f"evento {count}: {field} no finito")

        side = event.get("side")
        if action == "OPEN":
            if open_side is not None:
                issues.append(f"evento {count}: OPEN con posición ya abierta")
            elif side in _ALLOWED_SIDES:
                open_side = side
        elif action in {"CLOSE", "STOP_LOSS"}:
            if open_side is None:
                issues.append(f"evento {count}: {action} sin posición abierta")
            elif side in _ALLOWED_SIDES and side != open_side:
                issues.append(f"evento {count}: {action} side no coincide con OPEN")
            elif open_side is not None and side in _ALLOWED_SIDES:
                open_side = None

    if open_side is not None:
        # Una posición abierta al final es válida; solo se mantiene como estado.
        pass

    return PaperAuditResult(valid=not issues, event_count=count, issues=tuple(issues))


__all__ = ["PaperAuditResult", "audit_paper_events"]
