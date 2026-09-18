"""Pruebas de límites de ejecución y portafolio virtual."""

import pytest

from backtesting.models import PositionSide
from execution.interface import ExecutionRequest, ExecutionSide
from paper_trading.portfolio import PaperPortfolio
from risk.kill_switch import KillSwitch


@pytest.mark.parametrize("value", [True, "100", None, float("nan"), float("inf")])
def test_portfolio_rejects_invalid_initial_balance(value: object) -> None:
    with pytest.raises(ValueError):
        PaperPortfolio(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [True, "1", None, float("nan")])
def test_portfolio_rejects_invalid_price(value: object) -> None:
    portfolio = PaperPortfolio()
    with pytest.raises(ValueError):
        portfolio.open_position(PositionSide.BUY, value, 1.0)  # type: ignore[arg-type]


@pytest.mark.parametrize("reason", [True, "", "   ", None, 123])
def test_kill_switch_requires_non_empty_text(reason: object) -> None:
    switch = KillSwitch()
    with pytest.raises(ValueError):
        switch.trigger(reason)  # type: ignore[arg-type]


@pytest.mark.parametrize("quantity", [True, "1", None, float("nan")])
def test_execution_request_rejects_invalid_quantity(quantity: object) -> None:
    with pytest.raises(ValueError):
        ExecutionRequest("TEST", ExecutionSide.BUY, quantity)  # type: ignore[arg-type]
