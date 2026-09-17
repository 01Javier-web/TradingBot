"""Pruebas de límites de riesgo explícitos."""

from math import inf, nan

import pytest

from risk.limits import RiskLimits, risk_budget


def test_risk_budget_uses_balance_percentage() -> None:
    limits = RiskLimits(max_risk_per_trade=0.01)
    assert risk_budget(10_000, limits) == pytest.approx(100)


@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_risk_limits_reject_non_finite_percentages(value: float) -> None:
    with pytest.raises(ValueError):
        RiskLimits(max_risk_per_trade=value)

    with pytest.raises(ValueError):
        RiskLimits(max_daily_loss=value)


@pytest.mark.parametrize("balance", [nan, inf, -inf, 0])
def test_risk_budget_rejects_non_finite_or_non_positive_balance(balance: float) -> None:
    with pytest.raises(ValueError):
        risk_budget(balance, RiskLimits())
