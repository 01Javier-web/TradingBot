"""Pruebas del gate de revisión humana."""

from ai.research_decision import build_research_decision
from ai.research_pipeline import run_research
from app.research_demo import synthetic_data
from backtesting.optimizer import ParameterGrid
from backtesting.walk_forward_validation import WalkForwardValidation


def _run():
    return run_research(
        synthetic_data(80),
        ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,), rsi_periods=(14,)),
    )


def test_clean_research_does_not_require_review() -> None:
    result = build_research_decision(_run())

    assert result.review_required is False
    assert result.reasons == ()


def test_invalid_research_requires_review() -> None:
    run = _run()
    invalid = run.__class__(
        results=run.results,
        finding=run.finding,
        evidence=run.evidence.__class__(
            validation=run.evidence.validation.__class__(False, ("error",)),
            candidates=(),
        ),
        manifest=run.manifest,
        experiment_id=run.experiment_id,
    )

    result = build_research_decision(invalid)

    assert result.review_required is True
    assert result.reasons


def test_walk_forward_problem_requires_review() -> None:
    result = build_research_decision(
        _run(),
        WalkForwardValidation(False, 2, ("problema temporal",)),
    )

    assert result.review_required is True
    assert any("walk-forward" in reason for reason in result.reasons)
