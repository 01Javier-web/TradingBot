"""Prueba end-to-end del pipeline de TradingBot en modo simulation-first."""

from __future__ import annotations

import pandas as pd

from ai.coordinator import Coordinator
from analytics.paper_status import build_paper_status
from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from risk.manager import RiskConfig, RiskManager
from strategy.signals import Signal, generate_signals


def _trend_data(rows: int = 80) -> pd.DataFrame:
    close = pd.Series(range(1, rows + 1), dtype=float)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="h"),
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
        }
    )


def test_full_pipeline_strategy_to_paper_status() -> None:
    # 1. Datos -> indicadores -> señal.
    data = _trend_data()
    enriched = generate_signals(data)
    row = enriched.iloc[-1]
    assert row["signal"] == Signal.BUY

    # 2. La capa de análisis observa la señal, pero no ejecuta órdenes.
    analysis = Coordinator().analyze(row)
    assert analysis.recommendation == "BUY"
    assert analysis.market.confidence == 1.0

    # 3. Risk Manager -> Paper Trading: la operación solo existe en memoria.
    portfolio = PaperPortfolio(10_000)
    risk = RiskManager(RiskConfig(max_risk_per_trade=0.01))
    engine = PaperTradingEngine(portfolio, risk, quantity=1)
    result = engine.process(row)

    assert result == "OPEN BUY"
    assert portfolio.position is not None
    assert portfolio.position.side.value == "BUY"
    assert portfolio.position.stop_loss is not None
    assert engine.history[-1]["action"] == "OPEN"

    # 4. Analytics refleja la operación virtual abierta.
    status = build_paper_status(
        portfolio,
        engine.history,
        mark_price=float(row["close"]) + 0.5,
    )
    assert status.position == "BUY"
    assert status.event_counts == {"OPEN": 1}
    assert status.equity > status.balance
    assert status.unrealized_pnl > 0
    assert status.kill_switch_active is False
