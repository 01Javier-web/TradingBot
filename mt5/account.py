"""Funciones de lectura de información de la cuenta MT5.

Esta capa es únicamente de lectura: no abre, modifica ni cierra operaciones.
"""

import MetaTrader5 as mt5


def get_account_info():
    """Devuelve la información de la cuenta conectada o None si falla."""
    return mt5.account_info()
