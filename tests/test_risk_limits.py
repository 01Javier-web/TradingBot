"""Pruebas de límites de riesgo explícitos."""

import pytest

from risk.limits import RiskLimits, risk_budget


def test_risk_budget_uses_balance_percentage() -> None:
    limits = RiskLimits(max_risk_per_trade=0.01)
    assert risk_budget(10_000, limits) == pytest.approx(100)


def test_risk_budget_rejects_invalid_balance() -> None:
    with pytest.raises(ValueError):
        risk_budget(0, RiskLimits())
