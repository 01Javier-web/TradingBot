"""Lectura de mercado mediante la API de MetaTrader 5."""

from __future__ import annotations

from datetime import datetime
from numbers import Integral

import MetaTrader5 as mt5


class MT5MarketData:
    """Adaptador de solo lectura para ticks y velas de MT5."""

    @staticmethod
    def _validate_symbol(symbol: str) -> None:
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("symbol no puede estar vacío")

    @staticmethod
    def _validate_count(count: int) -> None:
        if isinstance(count, bool) or not isinstance(count, Integral) or count <= 0:
            raise ValueError("count debe ser un entero mayor que 0")

    @staticmethod
    def _validate_timeframe(timeframe: int) -> None:
        if isinstance(timeframe, bool) or not isinstance(timeframe, Integral) or timeframe <= 0:
            raise ValueError("timeframe debe ser un entero mayor que 0")

    def symbol_info(self, symbol: str):
        self._validate_symbol(symbol)
        return mt5.symbol_info(symbol)

    def tick(self, symbol: str):
        self._validate_symbol(symbol)
        return mt5.symbol_info_tick(symbol)

    def candles(self, symbol: str, timeframe: int, count: int = 100):
        self._validate_symbol(symbol)
        self._validate_timeframe(timeframe)
        self._validate_count(count)
        return mt5.copy_rates_from_pos(symbol, timeframe, 0, count)

    def candles_from(self, symbol: str, timeframe: int, start: datetime, count: int = 100):
        self._validate_symbol(symbol)
        self._validate_timeframe(timeframe)
        self._validate_count(count)
        if not isinstance(start, datetime):
            raise ValueError("start debe ser datetime")
        return mt5.copy_rates_from(symbol, timeframe, start, count)
