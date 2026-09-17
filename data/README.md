# Datos de mercado

Esta carpeta contiene la capa de entrada de datos del TradingBot.

- `market_data.py`: lectura de velas desde MetaTrader 5.
- `loader.py`: validación y normalización de datos históricos.
- `raw/` y `processed/` están ignoradas por Git porque los datos generados deben permanecer locales.

## Contrato mínimo de una vela

Los datos históricos deben incluir:

`time, open, high, low, close`

El cargador valida fechas y precios, ordena cronológicamente y elimina
registros duplicados por `time`.
