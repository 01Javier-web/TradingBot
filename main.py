"""Punto de entrada del TradingBot.

Etapa de infraestructura: conecta con MT5 y lee información de la cuenta.
No ejecuta operaciones.
"""

from mt5.account import get_account_info
from mt5.connection import initialize, last_error, shutdown


def main() -> None:
    print("TradingBot - diagnóstico MT5 (sin operaciones)")

    if not initialize():
        print("No se pudo inicializar MetaTrader 5.")
        print(f"Error MT5: {last_error()}")
        return

    try:
        print("MetaTrader 5 inicializado correctamente.")

        account = get_account_info()
        if account is None:
            print("No se pudo leer la información de la cuenta.")
            print(f"Error MT5: {last_error()}")
            return

        print(f"Cuenta: {account.login}")
        print(f"Servidor: {account.server}")
        print(f"Balance: {account.balance}")
        print(f"Equity: {account.equity}")
        print("Lectura de cuenta OK. No se ha enviado ninguna operación.")
    finally:
        shutdown()
        print("Conexión MT5 cerrada.")


if __name__ == "__main__":
    main()
