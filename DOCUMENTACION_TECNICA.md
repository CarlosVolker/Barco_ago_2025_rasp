# Documentación Técnica Completa: Sistema Vehículo IoT Genérico

Este documento profundiza en los detalles de implementación, seguridad, dependencias y protocolos del sistema. Destinado a auditores, integradores y desarrolladores.

## 1. Stack Tecnológico

### Software Base (Cliente Raspberry Pi)
*   **Lenguaje**: Python 3.9+ (Probado en 3.11).
*   **Sistema Operativo Recomendado**: Raspberry Pi OS (Bullseye/Bookworm), Lite o Desktop.
*   **Gestor de Paquetes**: `pip` (con entorno virtual `venv` recomendado).

### Librerías Críticas (Versiones)
| Librería | Versión | Propósito |
| :--- | :--- | :--- |
| `aiortc` | `1.6.0` | Stack WebRTC para video y data channels. |
| `aiohttp` | `3.9.3` | Cliente HTTP asíncrono para API REST. |
| `websockets` | `12.0` | Comunicación WebSocket cliente para señalización. |
| `opencv-python` | `4.9.0` | Captura y procesamiento de video. |
| `cryptography` | `45.0.0+` | Cifrado Fernet para almacenamiento de identidad. |
| `adafruit-circuitpython-pca9685` | `3.4.19` | Control I2C de la placa de servos. |
| `RPi.GPIO` | (Nativo) | Control GPIO directo para motores/relés. |

---

## 2. Sistema de Identidad y Seguridad

El proyecto abandona las claves estáticas (hardcoded) un modelo de **Identidad Criptográfica Vinculada al Hardware**.

### A. Almacenamiento Seguro (En el Vehículo)
*   **Archivo**: `.barco_identidad_segura` (Oculto en raíz).
*   **Permisos**: `600` (Solo lectura/escritura para el usuario root/pi).
*   **Algoritmo de Cifrado**: **Fernet (AES-128 en modo CBC con firma HMAC-SHA256)**.
*   **Llave de Cifrado (KDK)**: 
    *   No se guarda en disco.
    *   Se deriva dinámicamente usando **PBKDF2HMAC** (SHA256, 100k iteraciones).
    *   **Semilla (Salt)**: Estática (`b'barco_antigravity_salt'`).
    *   **Entropía Secreta**: **Número de Serie de la CPU** (`/proc/cpuinfo`).
    *   *Resultado*: Si alguien copia la tarjeta SD a otra Raspberry Pi, el archivo no se podrá descifrar.

### B. Proceso de Vinculación (Onboarding)
1.  **Generación**: El usuario crea un Token Corto (ej. "A1B2") en la Web.
2.  **Configuración**: El Token Corto se guarda en `.env` -> `BARCO_TOKEN_VINCULACION`.
3.  **Intercambio**: Al inicio, el script envía este token (vía HTTPS POST) a `/api/vehiculos/provisionar/`.
4.  **Emisión**: El servidor valida y retorna:
    *   `num_serie`: UUID público del vehículo.
    *   `token_secreto`: API Key de largo plazo (ej. `sk_live_...`).
5.  **Persistencia**: El script guarda estos datos cifrados y borra el token de vinculación de la memoria.

---

## 3. Protocolos de Comunicación

### A. WebRTC (Video y Control)
*   **Códecs de Video**: H.264 (Hardware) o VP8 (Software), negociado vía SDP.
*   **Data Channels**: Uso de canales SCTP para baja latencia.
    *   Etiqueta: `control`.
    *   Formato: JSON Strings.
    *   Orden: Ordered (TCP-like) o Unordered (UDP-like) configurable.
### C. Resiliencia en Redes 4G/5G (CGNAT)
Las redes móviles (como Entel Chile) utilizan **CGNAT (Carrier-Grade NAT)**, lo que impide que el barco tenga una IP pública accesible directamente. STUN a veces falla en estos entornos (NAT Simétrico).

**Solución Implementada**:
El sistema soporta configuración de servidor **TURN** (Traversal Using Relays around NAT).
1.  Si STUN falla (conexión peer-to-peer bloqueada), el barco intentará usar TURN.
2.  TURN actúa como un repetidor: `Barco -> Servidor TURN -> Navegador`.
3.  **Configuración**: Se define en `.env` con `SERVIDOR_TURN_URL`, `_USER` y `_PASS`.

**Recomendación de Infraestructura**:
*   Instalar **Coturn** en tu servidor (VPS/Coolify).
*   Abrir puertos UDP/TCP 3478 y rango 49152-65535.
*   Es la única forma garantizada de tener video fluido en 4G estricto.

### B. WebSockets (Señalización)
*   **Seguridad**: WSS (TLS 1.2+).
*   **Rol**: Intercambio de ofertas SDP (Session Description Protocol) y candidatos ICE.
*   **Autenticación**: Vía Query Param `?token={token_secreto}`.

---

## 4. Hardware Soportado

### Motores (Propulsión)
*   **Tipo**: Brushless con ESC (Electronic Speed Controller) o DC con Puente H.
*   **Señal**: PWM 50Hz.
*   **Mapeo**: 
    *   1.0ms (5% duty) = -100% (Reversa Máx).
    *   1.5ms (7.5% duty) = 0% (Neutro).
    *   2.0ms (10% duty) = +100% (Avance Máx).

### Servos (Dirección / PTZ)
*   **Driver Recomendado**: PCA9685 (I2C address `0x40`).
*   **Voltaje**: 5V - 6V (Alimentación externa recomendada, NO sacar de la Raspberry).
*   **Rango**: 0° a 180° mapeados a pulsos de 500us - 2500us.

---

## 5. Estructura de Archivos
```bash
/home/pi/proyecto
├── main.py                 # Orquestador del ciclo de vida (Asyncio Event Loop)
├── cliente_vehiculo.py     # Lógica de negocio, Red y FSM (Máquina de estados)
├── .env                    # Variables de entorno (URL Backend, Token Vinculación)
├── requirements.txt        # Lista de versiones congeladas
├── config/
│   ├── componentes.py      # Mapeo físico (Pines, Canales, Límites)
│   └── credenciales.py     # Cifrado y gestión de identidad
└── controladores/
    ├── instancias.py       # Factory de objetos de hardware
    ├── motor_brushless.py  # Driver ESC
    ├── actuador_servo.py   # Driver Servo Simple
    └── actuador_ejes.py    # Driver PTZ/Torretas
```
