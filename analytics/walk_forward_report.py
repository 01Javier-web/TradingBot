"""Resumen auditable de validaciones walk-forward."""

from __future__ import annotations

from typing import Any

from backtesting.walk_forward import WalkForwardWindow
from backtesting.walk_forward_validation import validate_walk_forward


def walk_forward_to_dict(windows: tuple[WalkForwardWindow, ...]) -> dict[str, Any]:
    """Convierte ventanas y su validación a una estructura serializable."""
    validation = validate_walk_forward(windows)
    return {
        "validation": {
            "valid": validation.valid,
            "windows": validation.windows,
            "issues": list(validation.issues),
        },
        "windows": [
            {
                "train_start": str(window.train_start),
                "train_end": str(window.train_end),
                "test_start": str(window.test_start),
                "test_end": str(window.test_end),
                "test_pnl": window.test_pnl,
            }
            for window in windows
        ],
    }
