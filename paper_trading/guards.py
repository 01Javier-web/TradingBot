"""Guardas para impedir que componentes de simulación reciban ejecución real."""

from __future__ import annotations


class SimulationOnlyViolation(RuntimeError):
    """Indica que un componente intentó cruzar la frontera de simulación."""


def assert_simulation_only(*, execution_authorized: bool, component: str) -> None:
    """Falla de forma explícita si un flujo declara autoridad de ejecución."""
    if execution_authorized:
        raise SimulationOnlyViolation(
            f"{component} no puede ejecutarse con autoridad de ejecución en simulation-first"
        )


__all__ = ["SimulationOnlyViolation", "assert_simulation_only"]
