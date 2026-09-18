"""Pruebas de validación estructural walk-forward."""

from backtesting.walk_forward import WalkForwardWindow
from backtesting.walk_forward_validation import validate_walk_forward


def _window(start: int, pnl: float = 1.0) -> WalkForwardWindow:
    return WalkForwardWindow(
        train_start=start,
        train_end=start + 2,
        test_start=start + 3,
        test_end=start + 4,
        test_pnl=pnl,
    )


def test_valid_windows_are_accepted() -> None:
    result = validate_walk_forward((_window(0), _window(5, -1.0)))

    assert result.valid is True
    assert result.windows == 2
    assert result.issues == ()


def test_overlapping_train_and_test_is_rejected() -> None:
    window = WalkForwardWindow(0, 5, 5, 7, 1.0)

    result = validate_walk_forward((window,))

    assert result.valid is False
    assert any("solapan" in issue for issue in result.issues)


def test_non_finite_pnl_is_rejected() -> None:
    window = _window(0, float("nan"))

    result = validate_walk_forward((window,))

    assert result.valid is False
    assert any("no es finito" in issue for issue in result.issues)


def test_test_windows_must_advance() -> None:
    result = validate_walk_forward((_window(0), _window(0)))

    assert result.valid is False
    assert any("avanzar estrictamente" in issue for issue in result.issues)


def test_empty_walk_forward_is_valid_but_contains_no_windows() -> None:
    result = validate_walk_forward(())

    assert result.valid is True
    assert result.windows == 0
    assert result.issues == ()


def test_non_tuple_windows_are_rejected() -> None:
    result = validate_walk_forward([])  # type: ignore[arg-type]
    assert result.valid is False
    assert "tupla" in result.issues[0]
