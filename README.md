# TradingBot

Bot de trading algorítmico con Python + MetaTrader 5.

## Estado actual

Proyecto en desarrollo con enfoque **simulation-first**. La infraestructura actual permite trabajar con datos, indicadores y señales sin enviar operaciones reales.

### Arquitectura

```text
market data
    ↓
strategy
    ↓
risk manager
    ↓
backtesting / paper trading
    ↓
MT5 (integración posterior)
```

La ejecución real no forma parte de esta etapa. Las credenciales y secretos deben mantenerse únicamente en variables de entorno locales y nunca deben subirse al repositorio.

## Desarrollo local

Instala las dependencias de `requirements.txt` y ejecuta los tests con:

```bash
python -m pytest
```

MetaTrader 5 debe estar instalado localmente para probar la integración de `mt5/`, pero las pruebas de estrategia no requieren enviar operaciones.
