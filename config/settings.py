"""Configuración base del TradingBot.

Las credenciales y secretos se cargarán desde variables de entorno.
Nunca deben escribirse directamente en el código ni subirse a GitHub.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    mt5_login: int | None = None
    mt5_server: str | None = None


def load_settings() -> Settings:
    login = os.getenv("MT5_LOGIN")
    return Settings(
        mt5_login=int(login) if login else None,
        mt5_server=os.getenv("MT5_SERVER"),
    )
