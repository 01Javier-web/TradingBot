"""Pruebas de validación estructural de entradas de riesgo."""

from risk.validation import validate_risk_inputs


def test_valid_risk_inputs_are_accepted() -> None:
    result = validate_risk_inputs(
        balance=10_000.0,
        risk_amount=50.0,
        daily_loss=20.0,
        open_positions=0,
        stop_loss_distance=10.0,
    )

    assert result.valid is True
    assert result.issues == ()


def test_non_finite_values_are_rejected() -> None:
    result = validate_risk_inputs(
        balance=float("nan"),
        risk_amount=50.0,
        daily_loss=float("inf"),
        open_positions=0,
        stop_loss_distance=10.0,
    )

    assert result.valid is False
    assert any("balance" in issue for issue in result.issues)
    assert any("daily_loss" in issue for issue in result.issues)


def test_invalid_counts_and_distances_are_rejected() -> None:
    result = validate_risk_inputs(
        balance=10_000.0,
        risk_amount=50.0,
        daily_loss=-1.0,
        open_positions=-1,
        stop_loss_distance=0.0,
    )

    assert result.valid is False
    assert any("daily_loss" in issue for issue in result.issues)
    assert any("open_positions" in issue for issue in result.issues)
    assert any("stop_loss_distance" in issue for issue in result.issues)
