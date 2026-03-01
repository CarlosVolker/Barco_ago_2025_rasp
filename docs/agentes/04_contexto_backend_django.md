# Contexto Backend Django (Control Plane)

## Rol del backend

Backend es control plane, no data plane de media:

- provisionamiento,
- autenticacion,
- signaling,
- telemetria,
- persistencia de estado.

Video y control en vivo deben ir por WebRTC P2P.

## Endpoints y contratos criticos

- `POST /api/vehiculos/provisionar/`
- `POST /api/vehiculos/telemetria/`
- `wss://.../ws/vehiculo/{num_serie}/?token={token}`

Referencia ampliada: `backend_spec.md` y `docs/7_contratos_y_capabilities_v1_0_0.md`.

## Ownership de integracion

- Formato inicio/capabilities: `src/edge_agent/runtime/legacy_adapter.py`
- Formato telemetria: `src/edge_agent/contracts/telemetry.py`
- Envelope signaling: `src/edge_agent/contracts/signaling.py`

## Do-not-break backend integration

1. No cambiar nombres de claves esperadas por backend sin migracion.
2. No remover `Authorization: Bearer` para telemetria.
3. No alterar semantica de 401/403 (revocacion local de identidad).
4. No romper idempotencia de reprovisionamiento en escenarios de reset.

## Pitfalls

- Backend guarda config de capacidades como texto en vez de JSON estructurado.
- Backend espera `intensidad_senal` cuando edge envia `intensidad_señal` por alias.
- Frontend consume shape viejo de `config` y falla render dinamico de controles.
