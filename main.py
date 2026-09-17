"""Punto de entrada del TradingBot.

En esta primera versión solo comprobamos que el proyecto puede cargar
la capa de conexión con MetaTrader 5. No ejecuta operaciones.
"""

from mt5.connection import initialize, shutdown, last_error


def main() -> None:
    print("TradingBot - modo inicial (sin operaciones reales)")

    if not initialize():
        print("No se pudo inicializar MetaTrader 5.")
        print(f"Error MT5: {last_error()}")
        return

    try:
        print("MetaTrader 5 inicializado correctamente.")
        print("Siguiente etapa: leer información de cuenta y mercado.")
    finally:
        shutdown()


if __name__ == "__main__":
    main()
