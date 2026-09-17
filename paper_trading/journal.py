"""Registro estructurado de eventos de paper trading."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass(frozen=True)
class TradeEvent:
    """Evento inmutable y serializable del ciclo de una operación."""

    timestamp: str
    event: str
    side: str | None = None
    price: float | None = None
    quantity: float | None = None
    pnl: float | None = None
    reason: str | None = None


class TradeJournal:
    """Acumula eventos en memoria y puede guardarlos como JSON Lines."""

    def __init__(self) -> None:
        self.events: list[TradeEvent] = []

    def record(self, event: str, **kwargs) -> TradeEvent:
        item = TradeEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event=event,
            **kwargs,
        )
        self.events.append(item)
        return item

    def save_jsonl(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            for event in self.events:
                handle.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
