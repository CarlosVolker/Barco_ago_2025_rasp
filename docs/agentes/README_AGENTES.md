# README para Agentes AI

Contexto minimo para modificar este repositorio sin romper operacion en campo.

## Orden de lectura obligatorio

1. `docs/agentes/01_contexto_edge_agent.md`
2. `docs/agentes/02_contexto_hardware_y_control.md`
3. `docs/agentes/03_contexto_red_webrtc_signaling.md`
4. `docs/agentes/04_contexto_backend_django.md`
5. `docs/agentes/05_contexto_pruebas_y_validacion.md`
6. `docs/agentes/06_historial_cambios_y_decisiones.md`
7. `docs/7_contratos_y_capabilities_v1_0_0.md`

## Regla principal

Este repo controla hardware real. Ante duda, priorizar safety:

- motores a 0 en error,
- no romper contratos,
- no cambiar mapping fisico sin validacion.

## Ownership rapido por dominios

- Runtime: `cliente_vehiculo.py`, `src/edge_agent/app.py`
- Contratos: `src/edge_agent/contracts/*`
- Hardware: `config/componentes.py`, `controladores/*`
- Identidad: `config/credenciales.py`, `src/edge_agent/identity/*`
- Red/WebRTC: `src/edge_agent/webrtc/*`, `src/edge_agent/video/*`

## Do-not-break universal para agentes

1. No cambiar semantica de comandos (`tipo`).
2. No cambiar payload envelope (`target/type/payload`).
3. No quitar `schema_version` de capacidades.
4. No eliminar failsafe de parada de motores.
5. No editar secretos ni subir archivos sensibles.
