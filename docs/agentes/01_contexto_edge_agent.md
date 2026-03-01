# Contexto Edge Agent

## Que hace el proceso principal

- `main.py` delega en `src/edge_agent/app.py`.
- `app.py` configura logging/settings, crea `ClienteVehiculo`, y gestiona shutdown con safety stop.
- `cliente_vehiculo.py` contiene bucles de signaling, ping, telemetria y creacion de peer WebRTC.

## Modulos PR-1/PR-2

- PR-1: flujo legacy en `cliente_vehiculo.py`.
- PR-2: contratos y componentes modulares en `src/edge_agent/*`.
- `src/edge_agent/runtime/legacy_adapter.py` conecta ambos mundos.

## Ownership por archivo (edge)

- `src/edge_agent/bootstrap/settings.py`: variables de entorno tipadas.
- `src/edge_agent/bootstrap/logging.py`: formato de logs.
- `src/edge_agent/capabilities/builder.py`: payload de capacidades.
- `src/edge_agent/runtime/legacy_adapter.py`: validacion control + telemetria + inicio.

## Do-not-break para cambios edge

1. Mantener `ClienteVehiculo.iniciar()` con gather de signaling + telemetria + ping.
2. Mantener reconexion WS y manejo 401/403 con revocacion local.
3. Mantener envio `inicio_vehiculo` al conectar signaling.
4. Mantener cierre ordenado de WebRTC/video en `liberar_recursos()`.

## Pitfalls

- Cambiar `asyncio.gather` por flujo secuencial bloquea tareas periodicas.
- Ignorar `except` de signaling puede dejar recursos vivos.
- Romper imports circulares entre `cliente_vehiculo.py` y `src/edge_agent/*`.
