"""Pruebas de auditoría estructural de eventos."""

from analytics.paper_audit import audit_paper_events


def test_audit_accepts_monotonic_structured_events() -> None:
    result = audit_paper_events([
        {"sequence": 1, "action": "OPEN", "price": 100.0, "quantity": 1.0, "stop_loss": 98.0},
        {"sequence": 2, "action": "CLOSE", "price": 102.0, "quantity": 1.0, "pnl": 2.0},
    ])

    assert result.valid
    assert result.event_count == 2
    assert result.issues == ()


def test_audit_rejects_sequence_gaps_and_unknown_actions() -> None:
    result = audit_paper_events([
        {"sequence": 1, "action": "OPEN"},
        {"sequence": 3, "action": "ALIEN"},
    ])

    assert not result.valid
    assert any("secuencia" in issue for issue in result.issues)
    assert any("acción" in issue for issue in result.issues)


def test_audit_rejects_non_finite_numeric_values() -> None:
    result = audit_paper_events([
        {"sequence": 1, "action": "REJECTED", "pnl": float("nan")},
    ])

    assert not result.valid
    assert any("no finito" in issue for issue in result.issues)
