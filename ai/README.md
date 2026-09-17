# Capa de IA

La capa `ai/` es observadora y analítica en esta fase.

## Regla de autoridad

Los agentes pueden analizar datos y generar propuestas, pero no pueden:

- enviar órdenes a MetaTrader 5;
- modificar límites del Risk Manager;
- acceder a credenciales o secretos;
- saltarse Paper Trading.

El flujo autorizado es:

```text
Market Data -> Strategy -> AI Analysis -> Risk Manager -> Paper Trading
```

La integración con un modelo LLM se añadirá posteriormente detrás de interfaces
controladas y con entradas/salidas estructuradas.
