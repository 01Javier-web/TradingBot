"""Pruebas del servicio de simulación."""

import pandas as pd

from app.simulation import SimulationService
from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio


def test_simulation_service_processes_ordered_dataframe() -> None:
    df = pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=2, freq="15min"),
            "open": [100.0, 101.0],
            "high": [101.0, 102.0],
            "low": [99.0, 100.0],
            "close": [100.5, 101.5],
            "signal": ["WAIT", "WAIT"],
        }
    )
    service = SimulationService(PaperTradingEngine(PaperPortfolio(10_000)))
    events = service.run(df)
    assert len(events) == 2
    assert all(event == "WAIT" for event in events)
