# Changelog

Este proyecto sigue un changelog orientado a operacion de campo y mantenimiento de agentes AI.

## [Unreleased]

### Added
- Documentacion operacional y de arquitectura modular para usuarios y agentes AI en `docs/` y `docs/agentes/`.
- Contratos formales de capacidades y comandos v1.0.0 documentados para frontend/backend/edge.
- Runbook de operacion con smoke tests para validar provisionamiento, signaling, WebRTC, control y telemetria.

### Changed
- `README.md` ahora incluye seccion de Arquitectura Modular (PR-1/PR-2), aclaracion P2P WebRTC y enlaces directos a documentacion.

## [1.4.0] - 2026-03-01

Hardening PR-4 con foco en observabilidad de runtime y perfiles de video adaptativos.

### Added
- Bucle de observabilidad en `cliente_vehiculo.py` para registrar snapshots periodicos de metricas en logs.
- Tests nuevos para perfiles de video y ruta minima de control/senalizacion:
  - `tests/test_video_pipeline_profiles.py`
  - `tests/test_cliente_signaling_control.py`

### Changed
- `VideoPipeline` ahora soporta perfiles `low`, `balanced`, `high` con cambio por `VIDEO_PROFILE`.
- Timeouts HTTP configurables por `TELEMETRY_REQUEST_TIMEOUT_S` en `EdgeSettings`.
- Parametros operativos nuevos en settings:
  - `OBSERVABILITY_LOG_INTERVAL_S`
  - `VIDEO_PROFILE`

## [1.3.0] - 2026-03-01

Hardening operativo PR-3 con foco en seguridad de control y resiliencia de red.

### Added
- Deadman timer asincrono en `src/edge_agent/safety/deadman.py` para detener motores cuando no llegan comandos frescos.
- Metrics collector liviano en `src/edge_agent/observability/metrics.py` para contadores/gauges/timestamps en proceso.
- Metodo `stop_all_motors()` en `src/edge_agent/control/runtime.py` para parada segura reutilizable.

### Changed
- Reconexion de signaling en `cliente_vehiculo.py` con backoff exponencial + jitter (1s a 30s) y reset tras conexion exitosa.
- Conexion WebSocket endurecida con `ping_interval=20`, `ping_timeout=20`, `close_timeout=5`.
- Reuso de una sola `aiohttp.ClientSession` para provisionamiento y telemetria.
- Intervalo de telemetria configurable por `TELEMETRY_INTERVAL_S` en vez de valor fijo.

### Safety
- En timeout de deadman o comando `parar`, los motores pasan a velocidad `0` sin cambiar el protocolo externo.

## [1.0.0] - 2026-03-01

Version base estabilizada de arquitectura modular Edge Agent.

### Added
- Bootstrapping modular en `src/edge_agent/bootstrap/` para settings tipados y logging estructurado JSON.
- Runtime de control separado en `src/edge_agent/control/runtime.py`.
- Pipeline de video separado en `src/edge_agent/video/pipeline.py`.
- Peer management WebRTC separado en `src/edge_agent/webrtc/peer_manager.py`.
- Contratos Pydantic para control, telemetria, signaling y capacidades en `src/edge_agent/contracts/`.
- Builder de capacidades con fingerprint de dispositivo en `src/edge_agent/capabilities/builder.py`.
- Adaptador de compatibilidad en `src/edge_agent/runtime/legacy_adapter.py` para convivencia PR-1 y PR-2.

### Security
- Identidad cifrada ligada a hardware conservada en `config/.barco_identidad_segura` via `config/credenciales.py`.

### Notes
- El canal de datos y video de operacion en vivo es WebRTC P2P (DTLS/SRTP).
- El backend Django opera como control plane (autenticacion, signaling, provisionamiento, telemetria), no como plano de media.

## [0.9.x]

### Added
- Cliente operativo inicial con provisionamiento, signaling WebSocket y telemetria periodica.
- Drivers de hardware genericos en `controladores/` y configuracion fisica en `config/componentes.py`.
- Instalacion para Raspberry Pi y optimizacion de baja latencia con `rpicam-vid`.
