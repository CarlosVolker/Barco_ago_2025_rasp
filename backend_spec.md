# Especificación Técnica del Backend: Vehículo IoT Genérico

Esta documentación es la "Biblia" para desarrollar el backend. Define todos los puntos de contacto entre el Vehículo (Raspberry Pi) y el Servidor (Django/Node/Etc).

## 1. Protocolos de Comunicación

El sistema híbrido utiliza dos vías de comunicación simultáneas:

| Protocolo | Uso Principal | Características |
| :--- | :--- | :--- |
| **HTTP/REST** | Configuración y Telemetría | Unidireccional (Vehículo -> Server), Lento, Seguro, Persistente. |
| **WebSockets** | Control y Video | Bidireccional (Full Duplex), Tiempo Real, Alta Velocidad. |

---

## 2. API REST (Endpoints para el Vehículo)

Estos endpoints son **consumidos por el script Python** en la Raspberry Pi.

### A. Aprovisionamiento (Onboarding)
*   **Método/URL**: `POST /api/vehiculos/provisionar/`
*   **Quién lo llama**: El vehículo, SOLO la primera vez que se enciende (o tras un factory reset).
*   **Payload (JSON)**:
    ```json
    {
        "token_vinculacion": "XYZ-123" // Token efímero generado por el usuario en el dashboard web.
    }
    ```
*   **Respuesta Exitosa (200 OK)**:
    ```json
    {
        "num_serie": "VEHICULO-ABC-001", // ID único asignado por el sistema
        "token_secreto": "sk_live_..."    // Llave maestra para futuras conexiones
    }
    ```
*   **Acción del Backend**: 
    1. Buscar usuario dueño del `token_vinculacion`.
    2. Crear registro en BD `Vehiculo`.
    3. Invalidad token de vinculación.

### B. Telemetría (Estado)
*   **Método/URL**: `POST /api/vehiculos/telemetria/`
*   **Quién lo llama**: El vehículo, cada 10 segundos (bucle de fondo).
*   **Headers**: `Authorization: Bearer <token_secreto>`
*   **Payload (JSON)**:
    ```json
    {
        "num_serie": "VEHICULO-ABC-001",
        "estado": "online",
        "bateria": 12.5,          // Voltaje actual
        "latitud": -33.4489,      // GPS
        "longitud": -70.6693,
        "intensidad_señal": -65   // dBm WiFi/4G
    }
    ```

---

## 3. WebSockets (Canal de Control Real-Time)

*   **URL**: `wss://tu-dominio.com/ws/vehiculo/{num_serie}/?token={token_secreto}`
*   **Rol**: Canal persistente para Señalización WebRTC e Intercambio de Configuración.

### A. Handshake Inicial (El vehículo se presenta)
Apenas se conecta el socket, el vehículo envía esto para decirle al backend "Qué soy".

*   **Mensaje (Vehículo -> Server)**:
    ```json
    {
        "type": "inicio_vehiculo",
        "payload": {
            "num_serie": "VEHICULO-ABC-001",
            "config": {
                // Esta estructura es EL PEGAMENTE del sistema genérico.
                // El backend debe guardarla en JSONB para que el Frontend sepa qué dibujar.
                "motores": [{"nombre": "propulsion_ppal"}],
                "servos_direccion": [{"nombre": "timon", "angulo_min": 45, "angulo_max": 135}],
                "actuadores_multieje": [
                    {
                        "nombre": "camara_ptz",
                        "canales": {"pan": 1, "tilt": 2}, 
                        "limites": {"pan": [0,180], "tilt": [45,135]}
                    }
                ]
            }
        }
    }
    ```

### B. Protocolo de Comandos de Control (Frontend -> Backend -> Vehículo)
Estos comandos viajan por el **DataChannel de WebRTC** (preferible) o por el **WebSocket**.

**1. Movimiento Básico (Arcade)**
Para autos o barcos simples.
```json
{
    "tipo": "movimiento",
    "velocidad": 100, // -100 (Atrás) a 100 (Adelante)
    "giro": 90        // 0 (Izq) - 90 (Centro) - 180 (Der)
}
```

**2. Motores Independientes (Tanques/Drones)**
Para control diferencial preciso.
```json
{
    "tipo": "motor_individual",
    "indice": 0,      // Indice en la lista 'motores' de la config
    "velocidad": 50
}
```

**3. Actuadores Multi-Eje (PTZ / Torretas)**
Para mover componentes complejos.
```json
{
    "tipo": "actuador_multieje",
    "indice": 0,      // Indice en lista 'actuadores_multieje' (ej. 0 = camara_ptz)
    "eje": "pan",     // Nombre del eje definido en config (pan, tilt, giro, elevacion)
    "angulo": 45,     // Grado absoluto
    "ejecutar_accion": false // True para disparar/actuar
}
```

**4. Parada de Emergencia**
```json
{
    "tipo": "parar"
}
```

---

## 4. Base de Datos Sugerida

### Tabla `Vehiculos`
*   `id`: PK
*   `num_serie`: String (Unique)
*   `configuracion_hardware`: JSONB (Guarda el payload del handshake inicial).
*   `usuario_id`: FK
*   `ultimo_heartbeat`: Timestamp

### Tabla `Telemetria` (TimescaleDB o similar)
*   `vehiculo_id`: FK
*   `bateria`: Float
*   `gps_lat`: Float
*   `gps_lon`: Float
*   `created_at`: Timestamp