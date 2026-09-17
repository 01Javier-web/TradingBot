# Backtesting

Módulo reservado para evaluar estrategias con datos históricos antes de
cualquier paper trading.

Principios:

1. No ejecutar órdenes reales durante el desarrollo del backtester.
2. Separar claramente datos históricos, señales, ejecución simulada y métricas.
3. Evitar usar información futura para generar una señal histórica.
4. Registrar costos y supuestos de simulación cuando se implemente el motor.
