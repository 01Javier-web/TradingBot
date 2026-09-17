"""Pruebas de entradas numéricas del motor de paper trading."""

from math import inf, nan

import pandas as pd
import pytest

from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from strategy.signals import Signal


@pytest.mark.parametrize("price", [nan, inf, -inf, 0.0, -1.0])
def test_engine_rejects_invalid_price_without_opening_position(price: float) -> None:
    portfolio = PaperPortfolio()
    engine = PaperTradingEngine(portfolio)

    result = engine.process(pd.Series({"close": price, "signal": Signal.BUY, "atr": 1.0}))

    assert result == "WAIT: precio inválido"
    assert portfolio.position is None


@pytest.mark.parametrize("atr", [nan, inf, -inf])
def test_engine_rejects_non_finite_atr_without_opening_position(atr: float) -> None:
    portfolio = PaperPortfolio()
    engine = PaperTradingEngine(portfolio)

    result = engine.process(pd.Series({"close": 100.0, "signal": Signal.BUY, "atr": atr}))

    assert result == "WAIT: ATR inválido"
    assert portfolio.position is None


def test_engine_keeps_zero_atr_as_risk_rejection() -> None:
    portfolio = PaperPortfolio()
    engine = PaperTradingEngine(portfolio)

    result = engine.process(pd.Series({"close": 100.0, "signal": Signal.BUY, "atr": 0.0}))

    assert result.startswith("REJECTED:")
    assert portfolio.position is None
