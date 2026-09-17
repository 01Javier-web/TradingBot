"""Pruebas de los límites duros del Risk Manager."""

import pytest

from risk.manager import RiskConfig, RiskManager


def test_approves_valid_trade() -> None:
    decision = RiskManager().approve(
        balance=10_000,
        risk_amount=50,
        daily_loss=20,
        open_positions=0,
        stop_loss_distance=10,
    )
    assert decision.approved is True


@pytest.mark.parametrize(
    "kwargs",
    [
        {"risk_amount": 200, "daily_loss": 0, "open_positions": 0, "stop_loss_distance": 10},
        {"risk_amount": 50, "daily_loss": 200, "open_positions": 0, "stop_loss_distance": 10},
        {"risk_amount": 50, "daily_loss": 0, "open_positions": 1, "stop_loss_distance": 10},
        {"risk_amount": 50, "daily_loss": 0, "open_positions": 0, "stop_loss_distance": None},
    ],
)
def test_rejects_risk_limit_violation(kwargs: dict) -> None:
    decision = RiskManager().approve(balance=10_000, **kwargs)
    assert decision.approved is False


def test_invalid_config_is_rejected() -> None:
    with pytest.raises(ValueError):
        RiskConfig(max_risk_per_trade=0)
