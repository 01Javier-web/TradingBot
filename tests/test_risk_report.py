"""Pruebas del reporte auditable de riesgo."""

from risk.manager import RiskDecision
from risk.validation import validate_risk_inputs
from analytics.risk_report import risk_decision_to_dict


def test_risk_report_preserves_decision_and_validation() -> None:
    validation = validate_risk_inputs(
        balance=10_000.0,
        risk_amount=50.0,
        daily_loss=20.0,
        open_positions=0,
        stop_loss_distance=10.0,
    )
    decision = RiskDecision(True, "operación aprobada por Risk Manager")

    report = risk_decision_to_dict(decision, validation)

    assert report["input_validation"]["valid"] is True
    assert report["approved"] is True
    assert report["reason"] == decision.reason
    assert report["execution_authorized"] is False
    assert report["mode"] == "simulation-first"


def test_risk_report_can_expose_validation_issues() -> None:
    validation = validate_risk_inputs(
        balance=0.0,
        risk_amount=50.0,
        daily_loss=0.0,
        open_positions=0,
        stop_loss_distance=10.0,
    )
    decision = RiskDecision(False, "balance inválido")

    report = risk_decision_to_dict(decision, validation)

    assert report["input_validation"]["valid"] is False
    assert report["input_validation"]["issues"]
    assert report["approved"] is False
