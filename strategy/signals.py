"""Generación de señales para una estrategia base de tendencia y momentum.

La estrategia es deliberadamente transparente y determinista. No ejecuta
órdenes ni contiene credenciales. Sus resultados deben validarse mediante
backtesting antes de considerar cualquier uso fuera de simulación.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import pandas as pd

from strategy.indicators import atr, ema, rsi


class Signal(str, Enum):
    """Señales posibles del motor de estrategia."""

    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"


@dataclass(frozen=True)
class StrategyConfig:
    """Parámetros explícitos de la estrategia base."""

    fast_ema_period: int = 20
    slow_ema_period: int = 50
    rsi_period: int = 14
    rsi_buy_level: float = 50.0
    rsi_sell_level: float = 50.0
    atr_period: int = 14
    min_atr: float = 0.0

    def __post_init__(self) -> None:
        _validate_config(self)


def add_indicators(df: pd.DataFrame, config: StrategyConfig | None = None) -> pd.DataFrame:
    """Añade indicadores a una copia del DataFrame sin modificar el original."""
    config = config or StrategyConfig()

    required = {"high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(sorted(missing))}")

    result = df.copy()
    result["ema_fast"] = ema(result["close"], config.fast_ema_period)
    result["ema_slow"] = ema(result["close"], config.slow_ema_period)
    result["rsi"] = rsi(result["close"], config.rsi_period)
    result["atr"] = atr(result, config.atr_period)
    return result


def generate_signal(row: pd.Series, config: StrategyConfig | None = None) -> Signal:
    """Genera BUY, SELL o WAIT para una vela ya enriquecida con indicadores.

    BUY: EMA rápida por encima de EMA lenta, RSI por encima del nivel de compra
    y ATR suficiente.

    SELL: EMA rápida por debajo de EMA lenta, RSI por debajo del nivel de venta
    y ATR suficiente.

    WAIT: cualquier condición incompleta o contradictoria.
    """
    config = config or StrategyConfig()

    required = ("ema_fast", "ema_slow", "rsi", "atr")
    if any(pd.isna(row.get(column)) for column in required):
        return Signal.WAIT

    if row["atr"] < config.min_atr:
        return Signal.WAIT

    if row["ema_fast"] > row["ema_slow"] and row["rsi"] > config.rsi_buy_level:
        return Signal.BUY

    if row["ema_fast"] < row["ema_slow"] and row["rsi"] < config.rsi_sell_level:
        return Signal.SELL

    return Signal.WAIT


def generate_signals(df: pd.DataFrame, config: StrategyConfig | None = None) -> pd.DataFrame:
    """Devuelve el DataFrame con indicadores y una columna ``signal``."""
    config = config or StrategyConfig()
    result = add_indicators(df, config)
    result["signal"] = result.apply(generate_signal, axis=1, config=config)
    return result


def _validate_config(config: StrategyConfig) -> None:
    periods = (
        config.fast_ema_period,
        config.slow_ema_period,
        config.rsi_period,
        config.atr_period,
    )
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in periods):
        raise ValueError("Los periodos deben ser enteros mayores que 0")
    if config.fast_ema_period >= config.slow_ema_period:
        raise ValueError("fast_ema_period debe ser menor que slow_ema_period")
    if not 0 <= config.rsi_buy_level <= 100 or not 0 <= config.rsi_sell_level <= 100:
        raise ValueError("Los niveles RSI deben estar entre 0 y 100")
    if config.min_atr < 0:
        raise ValueError("min_atr no puede ser negativo")
