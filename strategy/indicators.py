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

    # Cuando no hay pérdidas en la ventana, RSI = 100; cuando no hay
    # ganancias ni pérdidas, RSI = 50. Evitamos NaN en tendencias constantes.
    result = pd.Series(50.0, index=series.index, dtype=float)
    both_positive = (average_gain > 0) & (average_loss > 0)
    no_loss = (average_gain > 0) & (average_loss == 0)
    relative_strength = average_gain[both_positive] / average_loss[both_positive]
    result.loc[both_positive] = 100 - (100 / (1 + relative_strength))
    result.loc[no_loss] = 100.0
    return result


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
    if not isinstance(period, int) or isinstance(period, bool) or period <= 0:
        raise ValueError("period debe ser un entero mayor que 0")


def _require_columns(df: pd.DataFrame, columns: tuple[str, ...]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas: {', '.join(missing)}")
