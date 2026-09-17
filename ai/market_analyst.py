"""Analista de mercado determinista preparado para una futura capa LLM.

El agente produce observaciones, no órdenes. La autoridad de riesgo permanece
fuera de este módulo.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from strategy.signals import Signal


@dataclass(frozen=True)
class MarketAnalysis:
    signal: Signal
    trend: str
    momentum: str
    volatility: str
    confidence: float
    reasons: tuple[str, ...]


def analyze_row(row: pd.Series) -> MarketAnalysis:
    """Resume una vela enriquecida con indicadores sin ejecutar operaciones."""
    signal = row.get("signal", Signal.WAIT)
    if isinstance(signal, str):
        try:
            signal = Signal(signal)
        except ValueError:
            signal = Signal.WAIT

    ema_fast = row.get("ema_fast")
    ema_slow = row.get("ema_slow")
    rsi = row.get("rsi")
    atr_value = row.get("atr")

    reasons: list[str] = []
    if pd.notna(ema_fast) and pd.notna(ema_slow):
        trend = "bullish" if ema_fast > ema_slow else "bearish" if ema_fast < ema_slow else "neutral"
        reasons.append(f"EMA fast/slow: {trend}")
    else:
        trend = "unknown"

    if pd.notna(rsi):
        momentum = "positive" if rsi > 50 else "negative" if rsi < 50 else "neutral"
        reasons.append(f"RSI: {float(rsi):.2f}")
    else:
        momentum = "unknown"

    if pd.notna(atr_value):
        volatility = "active" if float(atr_value) > 0 else "flat"
    else:
        volatility = "unknown"

    confidence = 0.0
    if signal is not Signal.WAIT:
        confidence += 0.5
    if trend in ("bullish", "bearish"):
        confidence += 0.25
    if momentum in ("positive", "negative"):
        confidence += 0.25

    return MarketAnalysis(signal, trend, momentum, volatility, confidence, tuple(reasons))
