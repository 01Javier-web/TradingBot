"""Punto de entrada del TradingBot.

Etapa de infraestructura: diagnóstico de MT5 y lectura de cuenta.
No ejecuta operaciones.
"""

from mt5.account import get_account_info
from mt5.connection import initialize, is_connected, last_error, shutdown


def main() -> None:
    print("TradingBot - diagnóstico MT5 (sin operaciones)")
    print("Inicializando conexión...")

    if not initialize():
        print("ERROR: no se pudo inicializar MetaTrader 5.")
        print(f"Error MT5: {last_error()}")
        print("Verifica que MetaTrader 5 esté instalado y abierto.")
        return

    try:
        print("MetaTrader 5 inicializado correctamente.")

        if not is_connected():
            print("ERROR: MT5 se inicializó, pero el terminal no responde.")
            print(f"Error MT5: {last_error()}")
            return

        print("Terminal MT5 accesible.")

        account = get_account_info()
        if account is None:
            print("ERROR: no se pudo leer la información de la cuenta.")
            print(f"Error MT5: {last_error()}")
            return

        print(f"Cuenta: {account.login}")
        print(f"Servidor: {account.server}")
        print(f"Balance: {account.balance}")
        print(f"Equity: {account.equity}")
        print("Lectura de cuenta OK.")
        print("No se ha enviado ninguna operación.")
    finally:
        shutdown()
        print("Conexión MT5 cerrada.")


if __name__ == "__main__":
    main()
