"""Flujo de datos MT5 -> estrategia -> paper trading, sin órdenes reales."""

from __future__ import annotations

import pandas as pd

from data.market_data import get_candles
from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from risk.kill_switch import KillSwitch
from risk.manager import RiskManager
from strategy.signals import StrategyConfig, generate_signals


def run_mt5_snapshot(
    symbol: str,
    timeframe: int,
    *,
    count: int = 200,
    initial_balance: float = 10_000.0,
    quantity: float = 1.0,
    strategy: StrategyConfig | None = None,
    kill_switch: KillSwitch | None = None,
) -> list[str]:
    """Descarga un snapshot de velas y lo procesa únicamente en paper trading.

    La función no importa el adaptador de ejecución MT5 y, por diseño, no puede
    enviar órdenes al broker.
    """
    rates = get_candles(symbol, timeframe, count)
    if rates is None or len(rates) == 0:
        raise RuntimeError("MT5 no devolvió datos de mercado")

    frame = pd.DataFrame(rates)
    if "time" in frame.columns:
        frame["time"] = pd.to_datetime(frame["time"], unit="s", utc=True)

    enriched = generate_signals(frame, strategy)
    portfolio = PaperPortfolio(initial_balance)
    engine = PaperTradingEngine(portfolio, RiskManager(), quantity)

    if kill_switch is not None:
        kill_switch.check()

    return [engine.process(row) for _, row in enriched.iterrows()]
