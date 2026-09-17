"""Bucle controlado de paper trading sobre nuevas velas de MT5.

Solo consume datos. No existe ninguna llamada a order_send en este módulo.
"""

from __future__ import annotations

import time

import MetaTrader5 as mt5
import pandas as pd

from ai.coordinator import Coordinator
from data.market_data import get_candles
from paper_trading.engine import PaperTradingEngine
from risk.kill_switch import KillSwitch
from strategy.signals import StrategyConfig, generate_signals


class LivePaperRunner:
    """Procesa snapshots periódicos y conserva el estado virtual."""

    def __init__(
        self,
        engine: PaperTradingEngine,
        *,
        symbol: str = "EURUSD",
        timeframe: int = mt5.TIMEFRAME_M15,
        candles: int = 100,
        poll_seconds: int = 5,
        strategy: StrategyConfig | None = None,
        kill_switch: KillSwitch | None = None,
    ) -> None:
        if not symbol.strip():
            raise ValueError("symbol no puede estar vacío")
        if candles < 2 or poll_seconds <= 0:
            raise ValueError("candles debe ser >= 2 y poll_seconds > 0")
        self.engine = engine
        self.symbol = symbol
        self.timeframe = timeframe
        self.candles = candles
        self.poll_seconds = poll_seconds
        self.strategy = strategy or StrategyConfig()
        self.kill_switch = kill_switch or KillSwitch()
        self.coordinator = Coordinator()
        self.last_candle_time = None

    def process_once(self) -> str:
        """Lee una vela nueva y la procesa virtualmente si corresponde."""
        self.kill_switch.check()
        rates = get_candles(self.symbol, self.timeframe, self.candles)
        if rates is None or len(rates) == 0:
            raise RuntimeError("MT5 no devolvió datos de mercado")

        frame = pd.DataFrame(rates)
        frame["time"] = pd.to_datetime(frame["time"], unit="s", utc=True)
        latest = frame.iloc[-1]["time"]
        if latest == self.last_candle_time:
            return "WAIT: sin vela nueva"

        self.last_candle_time = latest
        enriched = generate_signals(frame, self.strategy)
        row = enriched.iloc[-1]
        analysis = self.coordinator.analyze(row)
        event = self.engine.process(row)
        return f"{latest.isoformat()} | signal={analysis.recommendation} | {event}"

    def run(self, iterations: int | None = None) -> list[str]:
        """Ejecuta iteraciones limitadas o hasta una interrupción del proceso."""
        results: list[str] = []
        completed = 0
        while iterations is None or completed < iterations:
            results.append(self.process_once())
            completed += 1
            if iterations is not None and completed >= iterations:
                break
            time.sleep(self.poll_seconds)
        return results
