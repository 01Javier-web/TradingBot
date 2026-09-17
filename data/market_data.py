"""Lectura de datos de mercado desde MetaTrader 5.

No ejecuta operaciones. La función devuelve velas OHLCV para que las capas
posteriores puedan analizarlas y, más adelante, hacer backtesting.
"""

from datetime import datetime

import MetaTrader5 as mt5


def get_candles(symbol: str, timeframe: int, count: int = 100):
    """Obtiene las últimas *count* velas del símbolo indicado.

    Retorna un numpy array de MT5 o None si MT5 no puede entregar los datos.
    """
    if count <= 0:
        raise ValueError("count debe ser mayor que 0")

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    return rates


def get_candles_from(symbol: str, timeframe: int, start: datetime, count: int = 100):
    """Obtiene velas comenzando desde una fecha/hora concreta."""
    if count <= 0:
        raise ValueError("count debe ser mayor que 0")

    return mt5.copy_rates_from(symbol, timeframe, start, count)
