"""Pruebas de validación del motor de paper trading."""

from math import inf, nan

import pandas as pd

from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from strategy.signals import Signal


def make_engine() -> PaperTradingEngine:
    return PaperTradingEngine(PaperPortfolio(10_000), quantity=1.0)


def test_invalid_price_is_rejected_without_action() -> None:
    engine = make_engine()
    result = engine.process(pd.Series({"signal": Signal.BUY, "close": nan, "atr": 1.0}))

    assert result == "WAIT: precio inválido"
    assert engine.portfolio.position is None
    assert engine.history[-1]["action"] == "REJECTED"
    assert engine.history[-1]["reason"] == "precio inválido"
    assert engine.history[-1]["sequence"] == 1


def test_invalid_signal_type_is_rejected() -> None:
    engine = make_engine()
    result = engine.process(pd.Series({"signal": 123, "close": 100.0, "atr": 1.0}))

    assert result == "WAIT: señal inválida"
    assert engine.portfolio.position is None


def test_non_finite_atr_is_rejected() -> None:
    engine = make_engine()
    result = engine.process(pd.Series({"signal": Signal.BUY, "close": 100.0, "atr": inf}))

    assert result == "WAIT: ATR inválido"
    assert engine.portfolio.position is None


def test_buy_with_stop_loss_below_zero_is_rejected() -> None:
    engine = make_engine()
    result = engine.process(pd.Series({"signal": Signal.BUY, "close": 1.0, "atr": 2.0}))

    assert result.startswith("REJECTED: stop-loss calculado inválido")
    assert engine.portfolio.position is None
