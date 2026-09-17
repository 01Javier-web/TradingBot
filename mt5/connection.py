"""Capa de conexión con MetaTrader 5.

Esta capa solo establece y cierra la conexión con el terminal.
No contiene lógica de trading ni envía órdenes.
"""

import MetaTrader5 as mt5


def initialize() -> bool:
    """Inicializa la conexión con el terminal MT5.

    MT5 debe estar instalado y, preferiblemente, abierto antes de ejecutar
    el bot. No se pasan credenciales ni se realizan operaciones aquí.
    """
    return bool(mt5.initialize())


def shutdown() -> None:
    """Cierra la conexión con MT5."""
    mt5.shutdown()


def last_error():
    """Devuelve el último error reportado por la API de MT5."""
    return mt5.last_error()


def is_connected() -> bool:
    """Comprueba si la API puede obtener información del terminal."""
    return mt5.terminal_info() is not None
