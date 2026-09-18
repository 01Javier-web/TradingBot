"""Pruebas de límites de ejecución y portafolio virtual."""

import pytest

from backtesting.models import PositionSide
from execution.interface import ExecutionRequest, ExecutionSide
from execution.mt5 import MT5ExecutionAdapter
from execution.paper import PaperExecutionAdapter
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


def test_mt5_adapter_cannot_be_created_with_order_authorization() -> None:
    with pytest.raises(ValueError, match="bloqueada"):
        MT5ExecutionAdapter(allow_orders=True)


def test_mt5_adapter_always_rejects_execution() -> None:
    adapter = MT5ExecutionAdapter()
    request = ExecutionRequest("TEST", ExecutionSide.BUY, 1.0)

    result = adapter.execute(request)

    assert result.accepted is False
    assert result.broker_order_id is None
    assert "bloqueada" in result.message


def test_paper_adapter_never_contacts_a_broker() -> None:
    adapter = PaperExecutionAdapter(PaperPortfolio())
    request = ExecutionRequest("TEST", ExecutionSide.BUY, 1.0)

    result = adapter.execute(request)

    assert result.accepted is False
    assert result.broker_order_id is None
    assert "requiere precio" in result.message
