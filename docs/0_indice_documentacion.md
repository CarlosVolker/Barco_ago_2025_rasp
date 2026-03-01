# Indice de Documentacion

Este indice separa documentacion para operadores/desarrolladores y para agentes AI.

## Lectura recomendada para humanos

1. `README.md` - vision general y arranque rapido.
2. `docs/4_instalacion.md` - instalacion en Raspberry Pi.
3. `docs/6_guia_rapida_nuevo_vehiculo.md` - onboarding de una unidad nueva.
4. `docs/8_runbook_operacion_y_smoke_tests.md` - operacion diaria y validacion.
5. `docs/5_arquitectura_modular_edge_agent.md` - limites por modulo y reglas de cambio.
6. `docs/7_contratos_y_capabilities_v1_0_0.md` - contratos de integracion frontend/backend/edge.

## Lectura recomendada para agentes AI

1. `docs/agentes/README_AGENTES.md` - orden de lectura y reglas de seguridad de cambios.
2. `docs/agentes/01_contexto_edge_agent.md` - flujo runtime principal y ownership de codigo.
3. `docs/agentes/02_contexto_hardware_y_control.md` - capas de control de hardware y riesgos.
4. `docs/agentes/03_contexto_red_webrtc_signaling.md` - signaling, ICE, TURN, P2P.
5. `docs/agentes/04_contexto_backend_django.md` - contrato de control plane con backend.
6. `docs/agentes/05_contexto_pruebas_y_validacion.md` - pruebas minimas para cambios seguros.
7. `docs/agentes/06_historial_cambios_y_decisiones.md` - decisiones PR-1/PR-2 y migracion.

## Mapa rapido por tema

- Arquitectura modular: `docs/5_arquitectura_modular_edge_agent.md`
- Migracion PR-1 -> PR-2: `docs/5_arquitectura_modular_edge_agent.md`
- Contratos y schema 1.0.0: `docs/7_contratos_y_capabilities_v1_0_0.md`
- Runbook operativo: `docs/8_runbook_operacion_y_smoke_tests.md`
- Vision y video: `docs/1_sistema_vision.md`
- Red y protocolos base: `docs/2_red_y_protocolos.md`
- Hardware y controladores: `docs/3_control_hardware.md`

## Estado de version documental

- Version de contratos vigente: `capabilities schema_version = 1.0.0`
- Este indice refleja arquitectura modular PR-1/PR-2 activa en `src/edge_agent/`.
