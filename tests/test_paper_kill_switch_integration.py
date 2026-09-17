"""Pruebas de integración del kill switch con paper trading."""

import pandas as pd

from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from risk.kill_switch import KillSwitch
from strategy.signals import Signal


def test_triggered_kill_switch_blocks_new_trade_and_records_event() -> None:
    switch = KillSwitch()
    switch.trigger("parada manual de seguridad")
    engine = PaperTradingEngine(
        PaperPortfolio(10_000),
        kill_switch=switch,
    )

    result = engine.process(
        pd.Series({"close": 100.0, "atr": 1.0, "signal": Signal.BUY})
    )

    assert result == "STOPPED: Kill switch activo: parada manual de seguridad"
    assert engine.portfolio.position is None
    assert engine.history == [
        {
            "sequence": 1,
            "action": "KILL_SWITCH",
            "price": None,
            "side": None,
            "quantity": None,
            "stop_loss": None,
            "pnl": None,
            "reason": "parada manual de seguridad",
        }
    ]


def test_kill_switch_does_not_close_or_modify_existing_virtual_position() -> None:
    switch = KillSwitch()
    engine = PaperTradingEngine(
        PaperPortfolio(10_000),
        kill_switch=switch,
        quantity=1,
    )

    assert engine.process(
        pd.Series({"close": 100.0, "atr": 5.0, "signal": Signal.BUY})
    ) == "OPEN BUY"

    switch.trigger("emergencia de simulación")
    result = engine.process(
        pd.Series({"close": 94.0, "signal": Signal.WAIT})
    )

    assert result == "STOPPED: Kill switch activo: emergencia de simulación"
    assert engine.portfolio.position is not None
    assert engine.portfolio.position.entry_price == 100.0
    assert engine.portfolio.balance == 10_000
    assert engine.history[-1]["action"] == "KILL_SWITCH"
    assert engine.history[-1]["reason"] == "emergencia de simulación"


def test_reset_allows_simulation_to_resume_explicitly() -> None:
    switch = KillSwitch()
    switch.trigger("pausa")
    engine = PaperTradingEngine(PaperPortfolio(10_000), kill_switch=switch)

    assert "STOPPED:" in engine.process(
        pd.Series({"close": 100.0, "atr": 1.0, "signal": Signal.BUY})
    )

    switch.reset()

    assert engine.process(
        pd.Series({"close": 100.0, "atr": 1.0, "signal": Signal.BUY})
    ) == "OPEN BUY"
