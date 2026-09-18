# TradingBot

Bot de trading algorítmico con Python + MetaTrader 5.

## Estado actual

Proyecto en desarrollo con enfoque **simulation-first**. La infraestructura permite trabajar con datos, indicadores, señales, backtesting y paper trading sin enviar operaciones reales.

### Flujo seguro actual

```text
market data
    ↓
validación OHLC
    ↓
strategy / indicadores / señales
    ↓
risk manager
    ↓
paper trading
    ↓
métricas y auditoría
```

La ejecución real **permanece bloqueada** en esta etapa. Ningún componente del flujo de paper trading recibe autoridad para enviar órdenes.

### Investigación reproducible

El proyecto incluye optimización controlada de parámetros, división cronológica train/test, fingerprint SHA-256 de datos, validación de resultados, evidencia, manifiestos y registro auditable de investigaciones.

### Desarrollo local

Instala las dependencias de `requirements.txt` y ejecuta los tests con:

```bash
python -m pytest
```

MetaTrader 5 puede estar instalado localmente para probar la lectura de mercado y la frontera de integración, pero el flujo de estrategia, backtesting y paper trading no envía órdenes.

## Próximas fases

1. Fortalecer el ciclo de paper trading y observabilidad.
2. Añadir pruebas end-to-end y escenarios de estrés.
3. Integrar lectura de mercado en tiempo real únicamente en modo lectura.
4. Evaluar estabilidad de estrategias con datos históricos y walk-forward.
5. Mantener la frontera de ejecución real cerrada hasta completar una revisión independiente de seguridad.
