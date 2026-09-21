"""Adaptador MT5 preparado para integración, sin envío de órdenes."""

from __future__ import annotations

import MetaTrader5 as mt5

from execution.interface import ExecutionRequest, ExecutionResult


class MT5ExecutionAdapter:
    """Puerta de entrada segura: esta primera versión solo valida disponibilidad.

    El método ``execute`` rechaza deliberadamente cualquier orden. La ejecución
    MT5 se habilitará únicamente después de completar las pruebas de Demo y la
    revisión de seguridad correspondiente.
    """

    def __init__(self, *, allow_orders: bool = False) -> None:
        if allow_orders:
            raise ValueError("La ejecución de órdenes MT5 está bloqueada en esta etapa")
        self.allow_orders = False

    def is_available(self) -> bool:
        """Indica si el terminal MT5 responde a la API."""
        return mt5.terminal_info() is not None

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Rechaza órdenes hasta que la integración pase la fase de validación."""
        if not isinstance(request, ExecutionRequest):
            raise TypeError("request debe ser ExecutionRequest")
        return ExecutionResult(False, "ejecución MT5 bloqueada: modo simulation-first")
