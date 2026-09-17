"""Pruebas del reporte del gate de revisión humana."""

from ai.research_decision import ResearchDecision
from analytics.research_decision_report import decision_to_dict


def test_decision_report_is_explicitly_non_operational() -> None:
    decision = ResearchDecision(False, ())

    report = decision_to_dict(decision)

    assert report == {
        "review_required": False,
        "reasons": [],
        "execution_authorized": False,
        "mode": "simulation-first",
    }


def test_decision_report_preserves_review_reasons() -> None:
    decision = ResearchDecision(True, ("problema de validación",))

    report = decision_to_dict(decision)

    assert report["review_required"] is True
    assert report["reasons"] == ["problema de validación"]
    assert report["execution_authorized"] is False
