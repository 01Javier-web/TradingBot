"""Indicadores técnicos puros basados en pandas."""

from __future__ import annotations

import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    """Media móvil simple."""
    _validate_period(period)
    return series.rolling(period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Media móvil exponencial."""
    _validate_period(period)
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index usando suavizado exponencial."""
    _validate_period(period)
    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    average_gain = gains.ewm(alpha=1 / period, adjust=False).mean()
    average_loss = losses.ewm(alpha=1 / period, adjust=False).mean()
    relative_strength = average_gain / average_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + relative_strength))


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range a partir de OHLC."""
    _validate_period(period)
    _require_columns(df, ("high", "low", "close"))
    previous_close = df["close"].shift(1)
    true_range = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - previous_close).abs(),
            (df["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def _validate_period(period: int) -> None:
    if not isinstance(period, int) or period <= 0:
        raise ValueError("period debe ser un entero mayor que 0")


def _require_columns(df: pd.DataFrame, columns: tuple[str, ...]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas: {', '.join(missing)}")
