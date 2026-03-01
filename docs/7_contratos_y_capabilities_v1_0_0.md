# Contratos y Capabilities v1.0.0

Especificacion practica de payloads que no deben romperse entre edge agent, backend y frontend.

## Alcance

- Control commands: `src/edge_agent/contracts/control.py`
- Signaling envelope: `src/edge_agent/contracts/signaling.py`
- Telemetria: `src/edge_agent/contracts/telemetry.py`
- Capabilities: `src/edge_agent/contracts/capabilities.py`
- Adaptacion de compatibilidad: `src/edge_agent/runtime/legacy_adapter.py`

## 1) Capabilities schema_version 1.0.0

El mensaje inicial incluye `config` con shape de `DeviceCapabilities`.

Campos obligatorios:

- `schema_version` (default actual: `1.0.0`)
- `device_id`
- `device_fingerprint`
- `motores[]`
- `servos_direccion[]`
- `actuadores_multieje[]`
- `camaras[]`

Ejemplo reducido:

```json
{
  "schema_version": "1.0.0",
  "device_id": "rpi-1a2b3c4d",
  "device_fingerprint": "rpi-1a2b3c4d5e6f7788",
  "motores": [{"nombre": "motor_principal", "canal": 12, "direccion_i2c": 64}],
  "servos_direccion": [{"nombre": "timon_central", "canal": 0, "angulo_min": 0, "angulo_max": 180, "direccion_i2c": 64}],
  "actuadores_multieje": [{"nombre": "camara_ptz", "canales": {"pan": 1, "tilt": 2}, "limites": {"pan": [0, 180], "tilt": [0, 180]}, "direccion_i2c": 64}],
  "camaras": [{"nombre": "frontal", "fps": 15, "resolucion": [640, 480], "tipo": "libcamera-csi"}]
}
```

## 2) Comandos de control (discriminador `tipo`)

### Movimiento basico

```json
{"tipo": "movimiento", "velocidad": 50, "giro": 90}
```

Reglas:

- `velocidad`: `-100..100`
- `giro`: `0..180`

### Motor individual

```json
{"tipo": "motor_individual", "indice": 0, "velocidad": 20}
```

Reglas:

- `indice >= 0`
- `velocidad`: `-100..100`

### Actuador multieje

```json
{"tipo": "actuador_multieje", "indice": 0, "eje": "pan", "angulo": 45, "ejecutar_accion": false}
```

Reglas:

- `angulo`: `0..180` cuando se envia.
- `eje` debe existir en `canales` del actuador objetivo.

### Parada

```json
{"tipo": "parar"}
```

## 3) Signaling envelope

Modelo canonico:

```json
{"target": "frontend-session-id", "type": "answer", "payload": {"sdp": "...", "type": "answer"}}
```

Notas:

- `target` puede ser `null` para broadcast/semantica server-side.
- `type` define el evento (`offer`, `answer`, `candidate`, `ping`, `pong`, `inicio_vehiculo`, etc).

## 4) Telemetria validada

Campos:

- `num_serie`
- `estado`
- `bateria`
- `latitud`
- `longitud`
- `intensidad_señal` (alias de campo interno `intensidad_senal`)
- `temperatura_cpu`
- `latencia` (`>= 0`)

Ejemplo:

```json
{
  "num_serie": "VEHICULO-ABC-001",
  "estado": "online",
  "bateria": 12.5,
  "latitud": -33.4489,
  "longitud": -70.6693,
  "intensidad_señal": -67,
  "temperatura_cpu": 55.2,
  "latencia": 83
}
```

## Versionado y compatibilidad

- Estado actual: `1.0.0`.
- Cambios aditivos permitidos: agregar campos opcionales, nunca renombrar campos existentes sin dual-stack.
- Cambios breaking: requieren nueva major y plan de convivencia.

## Do-not-break list de contratos

1. No renombrar `tipo` ni valores literales de comando.
2. No eliminar `schema_version` en capacidades.
3. No quitar alias `intensidad_señal` mientras backend lo use.
4. No cambiar `target/type/payload` de envelope.
5. No cambiar semantica de `indice` respecto al orden de `config/componentes.py`.

## Pitfalls de integracion

- Frontend mandando `giro` en rango `-100..100` en vez de `0..180`.
- Backend persistiendo `limites` como tupla string y no lista JSON numerica.
- Control por WS y DataChannel mezclando formatos (string JSON vs objeto) sin normalizar.
- Ignorar errores de validacion Pydantic y asumir que el comando fue aplicado.
