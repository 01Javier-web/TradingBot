"""Conteo de eventos de paper trading para observabilidad."""

from __future__ import annotations

from collections import Counter
from typing import Iterable


def summarize_events(events: Iterable[dict[str, object]]) -> dict[str, int]:
    """Cuenta eventos por tipo sin alterar el historial original."""
    return dict(Counter(str(event.get("action", "UNKNOWN")) for event in events))
