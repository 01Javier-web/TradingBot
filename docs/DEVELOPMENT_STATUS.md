# Estado de desarrollo

## Fase actual

Infraestructura + Market Data + Test Engineer.

## Completado

- Conexión MT5 aislada de la lógica de estrategia.
- Lectura de información de cuenta sin operaciones.
- Cargador CSV con validación básica de OHLC y tiempo.
- Indicadores SMA, EMA, RSI y ATR.
- Motor determinista inicial de señales BUY/SELL/WAIT.
- Paquetes base `risk/` y `backtesting/`.
- Plantilla `.env.example` sin secretos.
- Pruebas de indicadores, señales y datos de mercado.
- Flujo CI para ejecutar las pruebas del núcleo sin depender del terminal MT5.

## Pendiente

1. Confirmar las pruebas en el entorno local de desarrollo.
2. Completar el contrato de datos de mercado para casos reales de MT5.
3. Implementar backtesting sin look-ahead bias.
4. Implementar el Risk Manager con veto sobre ejecución.
5. Paper trading.
6. Integración avanzada con MT5 únicamente después de validar las fases anteriores.

## Regla de seguridad

Hasta completar las fases de validación, el proyecto permanece en modo
simulation-first y no debe enviar órdenes reales.
