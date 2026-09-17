"""Lectura de mercado mediante la API de MetaTrader 5."""

from __future__ import annotations

from datetime import datetime

import MetaTrader5 as mt5


class MT5MarketData:
    """Adaptador de solo lectura para ticks y velas de MT5."""

    def symbol_info(self, symbol: str):
        if not symbol.strip():
            raise ValueError("symbol no puede estar vacío")
        return mt5.symbol_info(symbol)

    def tick(self, symbol: str):
        if not symbol.strip():
            raise ValueError("symbol no puede estar vacío")
        return mt5.symbol_info_tick(symbol)

    def candles(self, symbol: str, timeframe: int, count: int = 100):
        if not symbol.strip():
            raise ValueError("symbol no puede estar vacío")
        if count <= 0:
            raise ValueError("count debe ser mayor que 0")
        return mt5.copy_rates_from_pos(symbol, timeframe, 0, count)

    def candles_from(self, symbol: str, timeframe: int, start: datetime, count: int = 100):
        if not symbol.strip():
            raise ValueError("symbol no puede estar vacío")
        if count <= 0:
            raise ValueError("count debe ser mayor que 0")
        return mt5.copy_rates_from(symbol, timeframe, start, count)
