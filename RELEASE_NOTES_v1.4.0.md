# v1.4.0 - PR-4 observability and adaptive video profiles

## Resumen
- PR-4 enfocado en robustez operativa: observabilidad periodica y perfiles de video adaptativos.
- Configuracion extendida para controlar timeout HTTP, perfil de video y frecuencia de snapshots.
- Nuevos tests unitarios para ruta de control y perfiles de video.
- Documentacion operativa y de decisiones actualizada para usuarios y agentes IA.

## Cambios principales

### 1) Observabilidad en runtime
- Se agrega un bucle de observabilidad en `cliente_vehiculo.py` que registra snapshots periodicos de metricas.
- Metricas utiles para operacion:
  - `control_commands_ok`
  - `control_commands_invalid`
  - `telemetry_sent`
  - `signaling_connections`
  - `deadman_timeouts`
  - `latency_ms` (gauge)

### 2) Perfiles de video adaptativos
- `src/edge_agent/video/pipeline.py` ahora soporta perfiles:
  - `low`
  - `balanced`
  - `high`
- Se habilita seleccion de perfil por entorno (`VIDEO_PROFILE`) para balancear calidad vs latencia segun red.

### 3) Settings operativos nuevos
En `src/edge_agent/bootstrap/settings.py`:
- `TELEMETRY_REQUEST_TIMEOUT_S`
- `OBSERVABILITY_LOG_INTERVAL_S`
- `VIDEO_PROFILE` (`low|balanced|high`)

### 4) Calidad y pruebas
Nuevos tests:
- `tests/test_video_pipeline_profiles.py`
- `tests/test_cliente_signaling_control.py`

Suite validada junto con PR-3:
- `tests/test_deadman_timer.py`
- `tests/test_control_runtime.py`
- `tests/test_video_pipeline_profiles.py`
- `tests/test_cliente_signaling_control.py`

### 5) Documentacion actualizada
- `CHANGELOG.md` con entrada `1.4.0`
- `docs/8_runbook_operacion_y_smoke_tests.md` con smoke tests PR-4
- `docs/agentes/06_historial_cambios_y_decisiones.md` con decisiones PR-4

## Impacto operativo
- Mejor visibilidad del estado del agente sin necesidad de stack externo.
- Ajuste rapido de perfil de video para redes moviles inestables.
- Base mas solida para monitoreo y troubleshooting en campo.

## Compatibilidad
- No cambia el protocolo externo principal de control/signaling.
- Mantiene arquitectura de media/control por WebRTC P2P.

## Recomendaciones de uso
- Perfil por defecto recomendado: `VIDEO_PROFILE=balanced`.
- En red movil inestable, usar `VIDEO_PROFILE=low`.
- Configurar `OBSERVABILITY_LOG_INTERVAL_S` entre `10` y `30` segundos para no saturar logs.
