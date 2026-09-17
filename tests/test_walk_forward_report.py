"""Pruebas del reporte serializable walk-forward."""

from backtesting.walk_forward import WalkForwardWindow
from analytics.walk_forward_report import walk_forward_to_dict


def test_walk_forward_report_contains_validation_and_windows() -> None:
    windows = (
        WalkForwardWindow(0, 2, 3, 4, 12.5),
        WalkForwardWindow(5, 7, 8, 9, -2.0),
    )

    report = walk_forward_to_dict(windows)

    assert report["validation"]["valid"] is True
    assert report["validation"]["windows"] == 2
    assert len(report["windows"]) == 2
    assert report["windows"][0]["test_pnl"] == 12.5
    assert report["windows"][1]["test_pnl"] == -2.0
