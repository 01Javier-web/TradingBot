"""Pruebas de las barreras de ejecución."""

from __future__ import annotations

from execution.interface import ExecutionRequest, ExecutionSide
from execution.mt5 import MT5ExecutionAdapter


def test_mt5_adapter_rejects_orders_by_default() -> None:
    adapter = MT5ExecutionAdapter()
    request = ExecutionRequest("EURUSD", ExecutionSide.BUY, 1.0, 1.0)
    result = adapter.execute(request)
    assert result.accepted is False
    assert "bloqueada" in result.message


def test_mt5_adapter_cannot_enable_orders() -> None:
    try:
        MT5ExecutionAdapter(allow_orders=True)
    except ValueError as exc:
        assert "bloqueada" in str(exc)
    else:
        raise AssertionError("El adaptador no debe permitir órdenes en esta etapa")


def test_execution_request_validates_quantity() -> None:
    try:
        ExecutionRequest("EURUSD", ExecutionSide.BUY, 0)
    except ValueError as exc:
        assert "quantity" in str(exc)
    else:
        raise AssertionError("quantity=0 debería ser rechazado")
