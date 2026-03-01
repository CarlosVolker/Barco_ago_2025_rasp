# Historial de Cambios y Decisiones (Agentes)

Documento corto para entender por que existen PR-1/PR-2 y que no debe revertirse accidentalmente.

## Decision 1: mantener `cliente_vehiculo.py` como orquestador legacy

- Motivo: evitar ruptura abrupta mientras se extraian modulos.
- Estado: vigente; convive con modulos en `src/edge_agent/`.

## Decision 2: introducir contratos tipados con Pydantic

- Motivo: frenar errores de integracion silenciosos.
- Implementacion: `src/edge_agent/contracts/*`.
- Impacto: comando/payload invalido se rechaza antes de tocar hardware.

## Decision 3: capacidades versionadas (`schema_version`)

- Motivo: permitir evolucion controlada de configuracion dinamica frontend.
- Implementacion: `src/edge_agent/contracts/capabilities.py` + builder.
- Version vigente: `1.0.0`.

## Decision 4: separar video/control/webrtc

- Motivo: aislar cambios de media de cambios de control de actuadores.
- Implementacion:
  - `src/edge_agent/video/pipeline.py`
  - `src/edge_agent/webrtc/peer_manager.py`
  - `src/edge_agent/control/runtime.py`

## Decision 5: backend como control plane

- Motivo: bajar latencia y costo de media.
- Consecuencia: WebRTC P2P para video/control; backend solo coordina.

## Decision 6 (PR-3): deadman timer y parada segura centralizada

- Motivo: evitar deriva de actuadores cuando se pierde flujo de comandos validos.
- Implementacion:
  - `src/edge_agent/safety/deadman.py`
  - `src/edge_agent/control/runtime.py::stop_all_motors()`
- Regla: timeout se dispara una sola vez y solo se rearma con `touch()`.

## Decision 7 (PR-3): reconexion WS con backoff exponencial + jitter

- Motivo: reducir tormentas de reconexion y mejorar resiliencia en redes moviles inestables.
- Implementacion: `cliente_vehiculo.py::conectar_signaling()`.
- Parametros: inicio 1s, maximo 30s, reset a 1s tras conexion exitosa.

## Decision 8 (PR-3): observabilidad local minima sin dependencias

- Motivo: tener trazabilidad de eventos criticos sin agregar stack externo.
- Implementacion: `src/edge_agent/observability/metrics.py`.
- Alcance: contadores, gauges y timestamps para control, signaling, telemetria y deadman.

## Migracion PR-1 -> PR-2

### Lo ya migrado

- Contratos tipados.
- Builder de capabilities.
- Adapter de compatibilidad de payloads.
- Bootstrap de settings/logging.

### Lo que sigue pendiente (recomendado)

- Reducir logica de red dentro de `cliente_vehiculo.py` hacia servicios dedicados.
- Agregar tests automaticos de contratos y parsing de comandos.
- Definir plan formal para `schema_version 1.1.0` o `2.0.0`.

## Do-not-break historico

1. No eliminar `legacy_adapter` hasta cerrar migracion completa backend/frontend.
2. No reemplazar `config/componentes.py` como fuente de verdad sin plan de transicion.
3. No remover manejo de revocacion de identidad en 401/403.
4. No quitar la llamada a `stop_all_motors()` en `StopCommand` ni en timeout de deadman.
5. No volver a sesiones HTTP efimeras por ciclo de telemetria.
6. No alterar contrato externo de signaling/control al endurecer runtime interno.

## Pitfalls historicos repetidos

- Cambios rapidos en payload de inicio sin coordinar frontend.
- Mezclar cambios de hardware y contratos en el mismo PR sin smoke tests.
- Tratar problemas de red 4G como bug de camara cuando era ausencia de TURN.
