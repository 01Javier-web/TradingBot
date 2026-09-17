"""Estado auditable y legible del motor de paper trading."""

from __future__ import annotations

from dataclasses import dataclass

from analytics.events import summarize_events
from paper_trading.portfolio import PaperPortfolio


@dataclass(frozen=True)
class PaperStatus:
    """Snapshot sin efectos secundarios del estado virtual."""

    balance: float
    equity: float
    unrealized_pnl: float
    position: str
    entry_price: float | None
    stop_loss: float | None
    quantity: float | None
    event_counts: dict[str, int]
    kill_switch_active: bool
    kill_switch_reason: str | None


def build_paper_status(
    portfolio: PaperPortfolio,
    events: list[dict[str, object]],
    mark_price: float | None = None,
    kill_switch_active: bool = False,
    kill_switch_reason: str | None = None,
) -> PaperStatus:
    """Construye un snapshot para consola, logs o una futura interfaz web."""
    position = portfolio.position
    if position is None:
        equity = portfolio.balance
        unrealized = 0.0
        side = "FLAT"
        entry = stop = quantity = None
    else:
        if mark_price is None:
            mark_price = position.entry_price
        equity = portfolio.mark_to_market(float(mark_price))
        unrealized = equity - portfolio.balance
        side = position.side.value
        entry = position.entry_price
        stop = position.stop_loss
        quantity = position.quantity

    return PaperStatus(
        balance=portfolio.balance,
        equity=equity,
        unrealized_pnl=unrealized,
        position=side,
        entry_price=entry,
        stop_loss=stop,
        quantity=quantity,
        event_counts=summarize_events(events),
        kill_switch_active=kill_switch_active,
        kill_switch_reason=kill_switch_reason,
    )


def format_paper_status(status: PaperStatus) -> str:
    """Formatea el snapshot en texto estable para consola."""
    lines = [
        "=== TRADINGBOT · PAPER STATUS ===",
        f"Balance virtual : {status.balance:.2f}",
        f"Equity virtual  : {status.equity:.2f}",
        f"PnL no realizado: {status.unrealized_pnl:.6f}",
        f"Posición        : {status.position}",
        f"Entrada         : {status.entry_price if status.entry_price is not None else '-'}",
        f"Stop loss       : {status.stop_loss if status.stop_loss is not None else '-'}",
        f"Cantidad        : {status.quantity if status.quantity is not None else '-'}",
        f"Eventos         : {status.event_counts or '-'}",
        f"Kill switch     : {'ACTIVO' if status.kill_switch_active else 'INACTIVO'}",
    ]
    if status.kill_switch_reason:
        lines.append(f"Motivo          : {status.kill_switch_reason}")
    return "\n".join(lines)
