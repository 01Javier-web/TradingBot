"""Puente de solo lectura entre MT5 y el flujo de paper trading."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from data.mt5_normalizer import normalize_market_rates
from execution.market import MT5MarketData


class PaperMarketFeed:
    """Obtiene velas de MT5 y las entrega como OHLC validado.

    La clase expone exclusivamente lectura de mercado. No contiene métodos de
    ejecución ni recibe un adaptador de órdenes.
    """

    def __init__(self, market_data: MT5MarketData | None = None) -> None:
        self.market_data = market_data or MT5MarketData()

    def latest(self, symbol: str, timeframe: int, count: int = 100) -> pd.DataFrame:
        """Lee las últimas velas y las normaliza antes de entregarlas."""
        rates = self.market_data.candles(symbol, timeframe, count)
        return normalize_market_rates(rates)

    def from_time(
        self,
        symbol: str,
        timeframe: int,
        start: datetime,
        count: int = 100,
    ) -> pd.DataFrame:
        """Lee velas desde una fecha y las normaliza antes de entregarlas."""
        rates = self.market_data.candles_from(symbol, timeframe, start, count)
        return normalize_market_rates(rates)


__all__ = ["PaperMarketFeed"]
