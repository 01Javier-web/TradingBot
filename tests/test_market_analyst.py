"""Pruebas del analista de mercado sin ejecución."""

import pandas as pd

from ai.market_analyst import analyze_row
from strategy.signals import Signal


def test_market_analyst_only_observes() -> None:
    row = pd.Series({"signal": Signal.BUY, "ema_fast": 110.0, "ema_slow": 100.0, "rsi": 60.0, "atr": 2.0})
    analysis = analyze_row(row)
    assert analysis.signal is Signal.BUY
    assert analysis.trend == "bullish"
    assert analysis.momentum == "positive"
    assert 0 <= analysis.confidence <= 1
