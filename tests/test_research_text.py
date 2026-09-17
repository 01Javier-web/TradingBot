"""Pruebas del formato textual de investigación."""

from ai.research_pipeline import run_research
from analytics.research_text import format_research_run
from app.research_demo import synthetic_data
from backtesting.optimizer import ParameterGrid


def _run():
    return run_research(
        synthetic_data(80),
        ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)),
    )


def test_format_research_run_contains_auditable_sections() -> None:
    report = format_research_run(_run())

    assert "=== TradingBot Research Report ===" in report
    assert "Resultados: 1" in report
    assert "Validación: OK" in report
    assert "Candidatos consistentes:" in report
    assert "Modo: simulation-first" in report
    assert "Ejecución real: BLOQUEADA" in report


def test_format_research_run_reports_validation_issues() -> None:
    run = _run()
    invalid = run.__class__(
        results=run.results,
        finding=run.finding,
        evidence=run.evidence.__class__(
            validation=run.evidence.validation.__class__(False, ("problema de prueba",)),
            candidates=(),
        ),
    )

    report = format_research_run(invalid)

    assert "Validación: ERROR" in report
    assert "- problema de prueba" in report
