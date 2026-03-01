# Arquitectura Modular Edge Agent (PR-1/PR-2)

Documento operativo para cambiar el agente sin romper compatibilidad con backend, frontend ni hardware.

## Objetivo

Separar responsabilidades del agente en modulos estables:

- `bootstrap`: configuracion y logging.
- `identity`: identidad del dispositivo.
- `contracts`: contratos de datos tipados.
- `capabilities`: construccion de capacidades declaradas.
- `control`: ejecucion de comandos fisicos.
- `video`: captura/track de video.
- `webrtc`: construccion del peer y data channel.
- `runtime`: puente de compatibilidad PR-1/PR-2.

## Plano de control vs plano de media

- Video y control en tiempo real via WebRTC P2P (DTLS/SRTP).
- Backend (Django u otro) funciona como control plane:
  - provisionamiento,
  - autenticacion,
  - signaling,
  - telemetria,
  - persistencia y trazabilidad.
- El backend no deberia ser el relay principal de video/control salvo fallback TURN.

## Ownership explicito por modulo (rutas)

### Entry point y orquestacion

- `main.py` -> wrapper de arranque.
- `src/edge_agent/app.py` -> ciclo de vida, señales de shutdown, safety stop.
- `cliente_vehiculo.py` -> cliente legacy principal, integra networking + runtime modular.

### Configuracion e identidad

- `src/edge_agent/bootstrap/settings.py` -> variables de entorno tipadas.
- `src/edge_agent/bootstrap/logging.py` -> logging JSON o fallback texto.
- `src/edge_agent/identity/device_id.py` -> fingerprint/device_id del equipo.
- `src/edge_agent/identity/credentials.py` -> facade identity.
- `config/credenciales.py` -> almacenamiento cifrado real y token de vinculacion.

### Contratos y compatibilidad

- `src/edge_agent/contracts/control.py` -> comandos `movimiento`, `motor_individual`, `actuador_multieje`, `parar`.
- `src/edge_agent/contracts/telemetry.py` -> payload telemetria validado.
- `src/edge_agent/contracts/signaling.py` -> envelope de señalizacion.
- `src/edge_agent/contracts/capabilities.py` -> schema de capacidades v1.0.0.
- `src/edge_agent/runtime/legacy_adapter.py` -> validacion/serializacion para convivencia con cliente legacy.

### Ejecucion de hardware y media

- `config/componentes.py` -> definicion fisica del vehiculo (fuente de verdad de hardware).
- `controladores/instancias.py` -> fabricas concretas desde `componentes.py`.
- `controladores/*.py` -> drivers concretos (motores, servos, PCA9685).
- `src/edge_agent/control/runtime.py` -> aplica comandos validados a instancias reales.
- `src/edge_agent/video/pipeline.py` -> captura camara y track WebRTC.
- `src/edge_agent/webrtc/peer_manager.py` -> ICE config y datachannel handlers.

## PR-1 -> PR-2 (notas de migracion)

## PR-1 (base)

- `cliente_vehiculo.py` concentraba logica de control, red, validacion y payloads.
- Configuracion y credenciales en modulos legacy (`config/*`, `controladores/*`).

## PR-2 (modularizacion)

- Se introduce `src/edge_agent/` con contratos tipados y separacion por dominio.
- `legacy_adapter` mantiene compatibilidad de payloads mientras se migra backend/frontend.
- `build_inicio_payload` ahora publica capacidades tipadas en `config` del mensaje inicial.
- `build_telemetry_payload` valida tipos antes de enviar al backend.

## Riesgos de migracion

- Cambiar shape JSON de inicio o telemetria rompe dashboards existentes.
- Cambiar `tipo` o rangos de comando rompe control remoto.
- Remover alias de `intensidad_señal` rompe ingestion backend si espera clave legacy.

## Do-not-break list

1. Mantener tipos de comando y nombres exactos: `movimiento`, `motor_individual`, `actuador_multieje`, `parar`.
2. Mantener contrato de signaling envelope: `{target, type, payload}`.
3. Mantener `schema_version: "1.0.0"` en capacidades hasta publicar version nueva.
4. Mantener `intensidad_señal` como alias de salida en telemetria.
5. Mantener failsafe: en desconexion, motores a `0` antes de cerrar peer.
6. Mantener compatibilidad de `config/componentes.py` como fuente de verdad para hardware.
7. Mantener soporte STUN/TURN por variables de entorno en entornos CGNAT.

## Errores comunes (pitfalls)

- **Editar solo frontend/backend y olvidar contratos Pydantic**: genera rechazo silencioso de comandos.
- **Subir velocidad de telemetria sin control**: aumenta ruido en backend y consumo de red movil.
- **Quitar TURN en 4G**: video parece intermitente o no conecta en NAT simetrico.
- **Modificar limites de servo sin validar fisico**: riesgo mecanico (topes).
- **Cambiar `config/credenciales.py` sin plan de migracion**: se pierde identidad local y re-provisiona.

## Estrategia de versionado recomendada

- Cambios compatibles: mantener `1.0.0` y documentar en changelog.
- Cambios aditivos en payloads: preparar `1.1.0` (backend tolerante a campos nuevos).
- Cambios breaking: publicar `2.0.0` y soportar dual-stack temporal via adapter.
