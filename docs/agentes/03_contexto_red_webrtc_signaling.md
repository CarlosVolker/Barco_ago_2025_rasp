# Contexto Red, WebRTC y Signaling

## Principio base

- Plano de media/control en vivo: WebRTC P2P.
- Plano de control: backend via REST + WebSocket.

## Flujo resumido

1. Vehiculo conecta a WebSocket signaling.
2. Envia `inicio_vehiculo` con capacidades.
3. Frontend/backend envian `offer`.
4. Edge responde `answer`.
5. ICE candidate exchange por signaling.
6. Comandos por DataChannel (preferido) o fallback WebSocket.

## Ownership por archivo

- WS + bucles de red: `cliente_vehiculo.py`
- Envelope de mensajes: `src/edge_agent/contracts/signaling.py`
- Config ICE/STUN/TURN: `src/edge_agent/webrtc/peer_manager.py`
- Track de video: `src/edge_agent/video/pipeline.py`

## Do-not-break red

1. Mantener URL de signaling en formato `.../ws/vehiculo/{num_serie}/?token=...`.
2. Mantener compatibilidad con `offer/answer/candidate/ping/pong`.
3. Mantener soporte TURN por variables `SERVIDOR_TURN_*`.
4. Mantener parsing robusto de candidate SDP.

## Pitfalls

- Asumir que STUN alcanza en 4G (suele fallar por CGNAT).
- Olvidar slash final en `URL_SIGNALING` y romper URL compuesta.
- Enviar payloads candidate incompletos (`sdpMid`, `sdpMLineIndex`).
