# Runbook de Operacion y Smoke Tests

Runbook para operacion diaria, incidentes y validacion rapida despues de cambios.

## Pre-vuelo (antes de salir a campo)

1. Verificar `.env` con backend correcto y TURN configurado.
2. Verificar `config/componentes.py` contra cableado real.
3. Verificar alimentacion externa de servos/ESC (no cargar todo por la Raspberry).
4. Ejecutar test local de hardware.

Comandos recomendados:

```bash
python test_hardware_mock.py
python test_teclado.py
python main.py
```

## Smoke tests minimos (orden sugerido)

### Smoke 1: Provisionamiento

- Condicion: identidad ausente.
- Accion: arrancar `python main.py` con `BARCO_TOKEN_VINCULACION` valido.
- Esperado: identidad guardada y log de registro exitoso.

### Smoke 2: Signaling WebSocket

- Condicion: identidad valida.
- Accion: abrir agente y revisar conexion WS.
- Esperado: evento `inicio_vehiculo` enviado sin error.

### Smoke 3: WebRTC video/control

- Accion: iniciar sesion desde frontend.
- Esperado:
  - llega `offer`,
  - agente responde `answer`,
  - video visible,
  - DataChannel con comandos funcional.

### Smoke 4: Telemetria

- Accion: esperar al menos un ciclo.
- Esperado: backend recibe payload con `latencia` e `intensidad_señal`.

### Smoke 5: Failsafe

- Accion: cerrar sesion/control remoto abruptamente.
- Esperado: motores quedan en velocidad `0` y recursos WebRTC se liberan.

### Smoke 6 (PR-3): Deadman timer

- Condicion: WebRTC activo y comandos de control detenidos por mas de `CONTROL_DEADMAN_MS`.
- Accion: dejar de enviar comandos de control manteniendo proceso vivo.
- Esperado:
  - log de warning por timeout deadman,
  - motores forzados a `0`,
  - no spam continuo del mismo warning hasta recibir comando valido nuevo.

### Smoke 7 (PR-3): Reconexion signaling robusta

- Condicion: agente conectado por WebSocket.
- Accion: cortar red o tumbar endpoint WS temporalmente.
- Esperado:
  - intentos de reconexion con espera creciente y jitter,
  - maximo de espera cercano a 30s,
  - al reconectar correctamente, siguiente fallo vuelve a empezar desde ~1s.

### Smoke 8 (PR-3): Telemetria y sesion HTTP reutilizada

- Accion: arrancar agente y observar ciclos de telemetria.
- Esperado:
  - frecuencia segun `TELEMETRY_INTERVAL_S`,
  - sin crear una sesion HTTP nueva por cada envio,
  - cierre limpio de sesion HTTP al finalizar el proceso.

### Smoke 9 (PR-4): Perfil de video configurable

- Accion: definir `VIDEO_PROFILE=low` en `.env` y reiniciar agente.
- Esperado:
  - log con inicio de camara usando perfil `low`,
  - bitrate y resolucion inferiores al perfil `balanced`,
  - control mantiene baja latencia aun con red inestable.

### Smoke 10 (PR-4): Snapshot de observabilidad

- Accion: ejecutar agente con `OBSERVABILITY_LOG_INTERVAL_S=10`.
- Esperado:
  - cada ~10s aparece log `Observability snapshot` con contadores/gauges,
  - se observan incrementos en `control_commands_ok`, `telemetry_sent`, `signaling_connections` segun actividad.

## Troubleshooting rapido

## No hay video

- Revisar disponibilidad de `rpicam-vid` en Raspberry.
- Revisar permisos/cable de camara CSI.
- Validar si se esta corriendo en Windows (usa `dshow` fallback).

## Hay signaling pero no conecta WebRTC

- Revisar `SERVIDOR_STUN` y `SERVIDOR_TURN_*`.
- En 4G/CGNAT, asumir TURN obligatorio.
- Revisar firewall/puertos en servidor TURN.

## Comandos llegan pero no se mueven actuadores

- Revisar indices y ejes definidos en `config/componentes.py`.
- Revisar que el comando cumpla contrato (`tipo`, rangos, indice).
- Revisar alimentacion de PCA9685/servos.

## Telemetria rechazada 401/403

- Token revocado o invalido.
- Regenerar identidad via reprovisionamiento controlado.

## Senales de log a observar en PR-3

- `Deadman timeout alcanzado, deteniendo motores por seguridad.`
- `Reintentando señalización en X.XX segundos...`
- `Conectado al servidor de señalización.`
- `Telemetría Rechazada (401/403). Revocando identidad local...`

## Ownership operativo por archivo

- Operacion de runtime: `cliente_vehiculo.py`, `src/edge_agent/app.py`
- Contratos de red: `src/edge_agent/contracts/*`
- Setup de red WebRTC: `src/edge_agent/webrtc/peer_manager.py`
- Video: `src/edge_agent/video/pipeline.py`
- Hardware: `config/componentes.py`, `controladores/*`
- Identidad: `config/credenciales.py`, `src/edge_agent/identity/*`

## Do-not-break en operacion

1. No desplegar sin prueba de parada de emergencia.
2. No cambiar `config/componentes.py` en campo sin test local.
3. No borrar identidad local por "prueba" en unidad productiva.
4. No asumir conectividad P2P en red movil sin TURN.
5. No subir cambios de contrato sin actualizar frontend/backend.

## Pitfalls frecuentes en incidentes

- Reiniciar proceso sin neutralizar motores primero.
- Mezclar `.env` de entornos (staging/prod).
- Cambiar canales PCA9685 y olvidar actualizar docs de mantenimiento.
- Diagnosticar problema de control sin revisar validaciones Pydantic.
