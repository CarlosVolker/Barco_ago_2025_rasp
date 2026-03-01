# v1.3.0 - Edge Agent modular + hardening

## Resumen
- Refactor del Edge Agent a arquitectura modular (`src/edge_agent/*`) manteniendo compatibilidad de runtime.
- Hardening PR-3: deadman timer, reconexion WS con backoff+jitter, reutilizacion de sesion HTTP y metricas locales.
- Migracion de controladores de motores/actuadores a PWM por hardware con PCA9685.
- Documentacion completa para operacion humana y contexto de agentes AI.
- Tests unitarios nuevos para `DeadmanTimer` y `ControlRuntime`.

## Cambios principales
### 1) Modularizacion del runtime
- Nuevo entrypoint modular: `src/edge_agent/app.py` (con `main.py` como wrapper).
- Separacion por dominios:
  - `src/edge_agent/control/`
  - `src/edge_agent/video/`
  - `src/edge_agent/webrtc/`
  - `src/edge_agent/contracts/`
  - `src/edge_agent/capabilities/`
  - `src/edge_agent/identity/`
  - `src/edge_agent/bootstrap/`
  - `src/edge_agent/runtime/`

### 2) Safety y resiliencia (PR-3)
- `DeadmanTimer` en `src/edge_agent/safety/deadman.py`.
- Parada segura centralizada con `stop_all_motors()` en `src/edge_agent/control/runtime.py`.
- WebSocket endurecido (`ping_interval`, `ping_timeout`, `close_timeout`) y reconexion exponencial con jitter.
- Reutilizacion de `aiohttp.ClientSession` para provisionamiento + telemetria.
- Telemetria configurable por `TELEMETRY_INTERVAL_S`.

### 3) Hardware PWM (PCA9685)
- Migracion de ESC/servos/actuadores para control por hardware.
- Nuevo gestor de placa: `controladores/pca9685_manager.py`.
- Configuracion de canales/direccion I2C consolidada en `config/componentes.py`.

### 4) Contratos y versionado
- Contratos tipados con Pydantic para control/senalizacion/telemetria/capabilities.
- `schema_version` de capabilities fijado en `1.0.0`.
- Identidad de dispositivo visible en formato corto (`rpi-xxxxxxxx`) y fingerprint largo interno.

### 5) Calidad y pruebas
- Tests agregados:
  - `tests/test_deadman_timer.py`
  - `tests/test_control_runtime.py`
- Ajuste de dependencia para compatibilidad SSL:
  - `cryptography==45.0.7`

## Documentacion
- `README.md` actualizado con arquitectura modular y flujo P2P.
- `CHANGELOG.md` actualizado.
- Nuevos docs operativos en `docs/`:
  - `docs/0_indice_documentacion.md`
  - `docs/5_arquitectura_modular_edge_agent.md`
  - `docs/6_guia_rapida_nuevo_vehiculo.md`
  - `docs/7_contratos_y_capabilities_v1_0_0.md`
  - `docs/8_runbook_operacion_y_smoke_tests.md`
- Contexto para agentes AI en `docs/agentes/*`.

## Notas operativas
- Video/control en vivo: **WebRTC P2P** (backend solo control plane).
- En entornos 4G/CGNAT, TURN sigue siendo recomendado.
- En entorno no-RPi se activa modo simulacion de hardware.
