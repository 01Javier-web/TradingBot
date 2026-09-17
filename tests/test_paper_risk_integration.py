"""Pruebas de integración entre Risk Manager y Paper Trading."""

import pandas as pd

from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from risk.manager import RiskConfig, RiskManager
from strategy.signals import Signal


def test_engine_rejects_trade_that_exceeds_risk_per_trade() -> None:
    engine = PaperTradingEngine(PaperPortfolio(10_000), quantity=1)

    result = engine.process(
        pd.Series({"close": 100.0, "atr": 101.0, "signal": Signal.BUY})
    )

    assert result == "REJECTED: supera el riesgo máximo por operación"
    assert engine.portfolio.position is None
    assert engine.history[-1]["action"] == "REJECTED"


def test_engine_rejects_trade_when_daily_loss_limit_is_already_reached() -> None:
    risk_manager = RiskManager(RiskConfig(max_daily_loss=0.02))
    engine = PaperTradingEngine(
        PaperPortfolio(10_000),
        risk_manager=risk_manager,
        quantity=1,
    )
    engine.daily_loss = 200.0

    result = engine.process(
        pd.Series({"close": 100.0, "atr": 1.0, "signal": Signal.BUY})
    )

    assert result == "REJECTED: límite de pérdida diaria alcanzado"
    assert engine.portfolio.position is None
    assert engine.history[-1]["reason"] == "límite de pérdida diaria alcanzado"


def test_engine_cannot_bypass_required_stop_loss() -> None:
    risk_manager = RiskManager(RiskConfig(stop_loss_required=True))
    engine = PaperTradingEngine(
        PaperPortfolio(10_000),
        risk_manager=risk_manager,
        quantity=1,
    )

    result = engine.process(
        pd.Series({"close": 100.0, "atr": 0.0, "signal": Signal.BUY})
    )

    assert result == "REJECTED: entradas de riesgo inválidas: risk_amount debe ser mayor que 0. stop_loss_distance debe ser mayor que 0."
    assert engine.portfolio.position is None
