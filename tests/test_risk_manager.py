"""Pruebas de configuración y decisiones del gestor de riesgo."""

from math import inf, nan

import pytest

from risk.manager import RiskConfig, RiskManager


def test_default_config_approves_trade_within_limits() -> None:
    decision = RiskManager().approve(
        balance=10_000.0,
        risk_amount=50.0,
        daily_loss=20.0,
        open_positions=0,
        stop_loss_distance=10.0,
    )

    assert decision.approved is True


def test_risk_per_trade_limit_is_hard() -> None:
    decision = RiskManager().approve(
        balance=10_000.0,
        risk_amount=100.01,
        daily_loss=0.0,
        open_positions=0,
        stop_loss_distance=10.0,
    )

    assert decision.approved is False
    assert "riesgo máximo" in decision.reason


def test_daily_loss_limit_is_hard() -> None:
    decision = RiskManager().approve(
        balance=10_000.0,
        risk_amount=10.0,
        daily_loss=200.0,
        open_positions=0,
        stop_loss_distance=10.0,
    )

    assert decision.approved is False
    assert "pérdida diaria" in decision.reason


def test_stop_loss_is_required_by_default() -> None:
    decision = RiskManager().approve(
        balance=10_000.0,
        risk_amount=10.0,
        daily_loss=0.0,
        open_positions=0,
        stop_loss_distance=None,
    )

    assert decision.approved is False


def test_non_numeric_inputs_are_rejected_without_type_error() -> None:
    decision = RiskManager().approve(
        balance="10000",  # type: ignore[arg-type]
        risk_amount=10.0,
        daily_loss=0.0,
        open_positions=0,
        stop_loss_distance=10.0,
    )

    assert decision.approved is False
    assert "entradas de riesgo inválidas" in decision.reason


@pytest.mark.parametrize("value", [nan, inf, -inf, 0.0, -0.01, True])
def test_invalid_risk_config_is_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        RiskConfig(max_risk_per_trade=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [nan, inf, -inf, 0.0, -0.01, True])
def test_invalid_daily_loss_config_is_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        RiskConfig(max_daily_loss=value)  # type: ignore[arg-type]


def test_max_open_positions_must_be_positive_integer() -> None:
    with pytest.raises(ValueError):
        RiskConfig(max_open_positions=0)
    with pytest.raises(ValueError):
        RiskConfig(max_open_positions=True)  # type: ignore[arg-type]


def test_stop_loss_required_must_be_boolean() -> None:
    with pytest.raises(ValueError):
        RiskConfig(stop_loss_required=1)  # type: ignore[arg-type]
