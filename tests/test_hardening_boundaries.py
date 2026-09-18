"""Pruebas de fronteras endurecidas del sistema simulation-first."""

from math import inf, nan

import pytest

from analytics.paper_json import _json_safe
from execution.interface import ExecutionRequest, ExecutionSide
from paper_trading.portfolio import PaperPortfolio
from backtesting.models import PositionSide
from risk.validation import validate_risk_inputs


@pytest.mark.parametrize("field,value", [
    ("balance", True),
    ("risk_amount", "50"),
    ("daily_loss", None),
    ("open_positions", True),
    ("open_positions", 1.5),
    ("stop_loss_distance", True),
])
def test_risk_validator_rejects_wrong_types(field: str, value: object) -> None:
    kwargs: dict[str, object] = {
        "balance": 10_000.0,
        "risk_amount": 50.0,
        "daily_loss": 20.0,
        "open_positions": 0,
        "stop_loss_distance": 10.0,
    }
    kwargs[field] = value

    result = validate_risk_inputs(**kwargs)

    assert result.valid is False


@pytest.mark.parametrize("kwargs", [
    {"symbol": "EURUSD", "side": "BUY", "quantity": 1.0},
    {"symbol": "EURUSD", "side": ExecutionSide.BUY, "quantity": nan},
    {"symbol": "EURUSD", "side": ExecutionSide.BUY, "quantity": inf},
    {"symbol": "EURUSD", "side": ExecutionSide.BUY, "quantity": True},
])
def test_execution_request_rejects_invalid_values(kwargs: dict[str, object]) -> None:
    with pytest.raises((TypeError, ValueError)):
        ExecutionRequest(**kwargs)


def test_execution_request_accepts_valid_request() -> None:
    request = ExecutionRequest(
        symbol="EURUSD",
        side=ExecutionSide.BUY,
        quantity=1.0,
        stop_loss=1.05,
    )

    assert request.symbol == "EURUSD"
    assert request.side is ExecutionSide.BUY


def test_portfolio_rejects_invalid_side() -> None:
    portfolio = PaperPortfolio()

    with pytest.raises(ValueError, match="side"):
        portfolio.open_position("BUY", 100.0, 1.0)  # type: ignore[arg-type]


def test_json_safe_converts_non_finite_values_recursively() -> None:
    payload = {
        "profit_factor": inf,
        "nested": {"loss": nan},
        "items": [1.0, inf],
    }

    assert _json_safe(payload) == {
        "profit_factor": None,
        "nested": {"loss": None},
        "items": [1.0, None],
    }
