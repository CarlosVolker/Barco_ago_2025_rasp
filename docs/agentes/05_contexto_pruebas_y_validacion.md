# Contexto de Pruebas y Validacion

## Objetivo

Detectar rapido regresiones en seguridad operacional, contratos y conectividad.

## Suite minima sugerida

### Pruebas locales sin backend

- `python test_hardware_mock.py` (carga de instancias y comandos basicos)
- `python test_teclado.py` (validacion manual de control)

### Pruebas con backend

- Arranque de agente `python main.py`
- Provisionamiento (si aplica)
- Signaling + oferta/respuesta
- Comando `parar`
- Envio de telemetria

## Validaciones de contratos

- Comandos invalidos deben rechazarse sin mover hardware.
- `build_telemetry_payload` debe serializar alias `intensidad_señal`.
- `build_inicio_payload` debe incluir `schema_version` de capacidades.

## Do-not-break de validacion

1. No omitir smoke de failsafe antes de publicar cambios.
2. No considerar "verde" si solo funciona en LAN y falla en 4G.
3. No introducir cambios de contratos sin prueba de roundtrip frontend/backend.

## Pitfalls

- Probar solo camino feliz y olvidar desconexion/reconexion.
- Ejecutar pruebas en entorno distinto al hardware real sin aclararlo.
- Ignorar warnings de validacion Pydantic en logs.
