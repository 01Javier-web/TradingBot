"""Conexión segura y mínima con MetaTrader 5."""

import MetaTrader5 as mt5


def initialize() -> bool:
    """Inicializa la conexión con el terminal MT5 abierto en el equipo."""
    return bool(mt5.initialize())


def shutdown() -> None:
    """Cierra la conexión con MT5."""
    mt5.shutdown()


def last_error():
    """Devuelve el último error reportado por la API de MT5."""
    return mt5.last_error()
