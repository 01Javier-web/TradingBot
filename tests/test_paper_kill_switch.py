"""Integración del kill switch con paper trading."""

import pandas as pd

from backtesting.models import PositionSide
from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from risk.kill_switch import KillSwitch


def test_active_kill_switch_blocks_paper_actions() -> None:
    switch = KillSwitch()
    switch.trigger("manual safety stop")
    engine = PaperTradingEngine(PaperPortfolio(), kill_switch=switch)
    row = pd.Series({"close": 100.0, "signal": "BUY", "atr": 1.0})

    result = engine.process(row)

    assert result.startswith("STOPPED:")
    assert engine.portfolio.position is None
    assert engine.history[-1]["action"] == "KILL_SWITCH"


def test_reset_allows_normal_paper_processing() -> None:
    switch = KillSwitch()
    switch.trigger("temporary")
    switch.reset()
    engine = PaperTradingEngine(PaperPortfolio(), kill_switch=switch)
    row = pd.Series({"close": 100.0, "signal": "BUY", "atr": 1.0})

    result = engine.process(row)

    assert result == "OPEN BUY"
    assert engine.portfolio.position is not None
    assert engine.portfolio.position.side is PositionSide.BUY
