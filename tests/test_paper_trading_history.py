"""Pruebas de trazabilidad estructurada del paper trading."""

import pandas as pd

from backtesting.models import PositionSide
from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from strategy.signals import Signal


def test_open_event_has_monotonic_sequence_and_trade_fields() -> None:
    engine = PaperTradingEngine(PaperPortfolio(10_000), quantity=1)

    result = engine.process(pd.Series({"close": 100.0, "atr": 1.0, "signal": Signal.BUY}))

    assert result == "OPEN BUY"
    assert engine.history == [
        {
            "sequence": 1,
            "action": "OPEN",
            "price": 100.0,
            "side": PositionSide.BUY.value,
            "quantity": 1.0,
            "stop_loss": 99.0,
            "pnl": None,
            "reason": None,
        }
    ]


def test_rejection_is_structured_and_sequenced() -> None:
    engine = PaperTradingEngine(PaperPortfolio(10_000))

    result = engine.process(pd.Series({"close": 100.0, "atr": float("nan"), "signal": Signal.BUY}))

    assert result == "WAIT: ATR inválido"
    assert engine.history[0]["sequence"] == 1
    assert engine.history[0]["action"] == "REJECTED"
    assert engine.history[0]["reason"] == "ATR inválido"


def test_stop_loss_event_contains_pnl_and_position_context() -> None:
    engine = PaperTradingEngine(PaperPortfolio(10_000), quantity=2)
    engine.process(pd.Series({"close": 100.0, "atr": 5.0, "signal": Signal.BUY}))

    result = engine.process(pd.Series({"close": 95.0, "signal": Signal.WAIT}))

    assert result == "STOP_LOSS BUY: pnl=-10.000000"
    assert engine.history[-1]["sequence"] == 2
    assert engine.history[-1]["action"] == "STOP_LOSS"
    assert engine.history[-1]["side"] == PositionSide.BUY.value
    assert engine.history[-1]["quantity"] == 2.0
    assert engine.history[-1]["pnl"] == -10.0
