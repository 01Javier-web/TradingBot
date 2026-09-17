"""Pruebas de las fronteras de ejecución."""

from execution.interface import ExecutionRequest, ExecutionResult, ExecutionSide
from execution.mt5 import MT5ExecutionAdapter


def test_execution_request_validates_quantity() -> None:
    try:
        ExecutionRequest("EURUSD", ExecutionSide.BUY, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("quantity inválida no fue rechazada")


def test_mt5_adapter_is_locked() -> None:
    adapter = MT5ExecutionAdapter()
    result = adapter.execute(ExecutionRequest("EURUSD", ExecutionSide.BUY, 1.0, 1.0))
    assert isinstance(result, ExecutionResult)
    assert result.accepted is False
    assert "bloqueada" in result.message
