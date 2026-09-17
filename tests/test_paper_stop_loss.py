"""Pruebas de protección de stop-loss en paper trading."""

import pandas as pd

from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from risk.manager import RiskManager
from strategy.signals import Signal


def test_stop_loss_closes_buy_position() -> None:
    portfolio = PaperPortfolio(1_000)
    engine = PaperTradingEngine(portfolio, RiskManager(), quantity=1)
    opened = engine.process(pd.Series({"close": 100.0, "signal": Signal.BUY, "atr": 5.0}))
    assert opened == "OPEN BUY"
    result = engine.process(pd.Series({"close": 94.0, "signal": Signal.WAIT, "atr": 5.0}))
    assert result.startswith("STOP_LOSS BUY")
    assert portfolio.position is None
    assert portfolio.balance == 995.0
    assert engine.history[-1]["action"] == "STOP_LOSS"
