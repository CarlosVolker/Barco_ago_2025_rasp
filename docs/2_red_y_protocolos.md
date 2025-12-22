# Documentación: Arquitectura de Red y Protocolos

El vehículo utiliza un sistema de comunicación híbrido para garantizar control en tiempo real y persistencia de datos.

## 1. API REST (HTTP/HTTPS)
Se utiliza para tareas de baja frecuencia, configuración inicial y reporte de estado.

### Aprovisionamiento (Onboarding)
*   **Endpoint**: `POST /api/vehiculos/provisionar/`
*   **Función**: Convierte un `TOKEN_VINCULACION` temporal (ingresado por el usuario) en credenciales permanentes.
*   **Respuesta**: Guarda localmente el `NUM_SERIE` y `TOKEN_SECRETO` en `.env`.

### Telemetría
*   **Endpoint**: `POST /api/vehiculos/telemetria/`
*   **Frecuencia**: Cada 10 segundos.
*   **Datos enviados**:
    *   Batería (Voltaje simulado/leído).
    *   Coordenadas GPS.
    *   Intensidad de señal WiFi (dBm).
    *   Estado (`online`).

## 2. WebSockets (Señalización)
Canal persistente para iniciar la videollamada y recibir comandos.

*   **Protocolo**: `wss://` (WebSocket Seguro).
*   **Autenticación**: El vehículo envía su `num_serie` y configuración de hardware al conectarse.

## 3. WebRTC (Video y Control Real-Time)
Es el núcleo del sistema de manejo. Permite video fluido y comandos instantáneos sin pasar por la base de datos del servidor.

### Canal de Datos (`DataChannel`)
Además del video, se abre un canal de datos bidireccional fiable para enviar comandos de control.

#### Formato de Comandos (JSON)

**Movimiento Básico (Arcade):**
```json
{
    "tipo": "movimiento",
    "velocidad": 100,  // -100 (Atrás) a 100 (Adelante)
    "giro": 0          // -100 (Izq) a 100 (Der)
}
```

**Control Individual de Motores:**
Para vehículos tipo tanque o con configuraciones complejas.
```json
{
    "tipo": "motor_individual",
    "indice": 0,       // ID del motor en la config
    "velocidad": 50
}
```

**Parada de Emergencia:**
```json
{
    "tipo": "parar"
}
```

### Seguridad
Toda la transmisión WebRTC (Video y Datos) viaja encriptada punto-a-punto (P2P) usando **DTLS/SRTP**.
