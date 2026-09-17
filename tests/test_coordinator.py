"""Pruebas del coordinador de análisis."""

import pandas as pd

from ai.coordinator import Coordinator
from strategy.signals import Signal


def test_coordinator_returns_analysis_without_execution() -> None:
    row = pd.Series({"signal": Signal.BUY, "ema_fast": 110.0, "ema_slow": 100.0, "rsi": 60.0, "atr": 2.0, "close": 110.0})
    report = Coordinator().analyze(row)
    assert report.recommendation == "BUY"
    assert report.market.trend == "bullish"
