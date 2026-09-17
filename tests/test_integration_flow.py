"""Prueba de integración del flujo Strategy -> AI -> Risk -> Paper Trading."""

import pandas as pd

from ai.coordinator import Coordinator
from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from risk.manager import RiskConfig, RiskManager
from strategy.signals import Signal


def test_signal_can_be_analyzed_and_risk_gated_before_paper_execution() -> None:
    row = pd.Series({"signal": Signal.BUY, "ema_fast": 110.0, "ema_slow": 100.0, "rsi": 60.0, "atr": 1.0, "close": 110.0, "time": pd.Timestamp("2026-01-01")})
    report = Coordinator().analyze(row)
    assert report.recommendation == "BUY"

    portfolio = PaperPortfolio(10_000)
    risk = RiskManager(RiskConfig(max_risk_per_trade=0.01))
    engine = PaperTradingEngine(portfolio, risk, quantity=1)
    result = engine.process(row)

    assert result == "OPEN BUY"
    assert portfolio.position is not None
    assert portfolio.position.side.value == "BUY"
