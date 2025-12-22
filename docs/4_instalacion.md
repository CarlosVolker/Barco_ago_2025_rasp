# Guía de Instalación y Despliegue

Instrucciones para preparar una Raspberry Pi (OS Bookworm o superior) para ejecutar el cliente del vehículo.

## 1. Requisitos del Sistema
*   **Hardware**: Raspberry Pi 3B+, 4 o 5.
*   **OS**: Raspberry Pi OS (Bookworm) - **Requerido para `rpicam-vid`**.
*   **Cámara**: Módulo Pi Camera conectado al puerto CSI.

## 2. Dependencias del Sistema (APT)
Es necesario instalar las librerías de multimedia y python venv.

```bash
sudo apt update
sudo apt install -y python3-venv libcamera-apps v4l-utils ffmpeg
```

## 3. Entorno Virtual Python
Se recomienda aislar las librerías del proyecto.

```bash
# Crear entorno
python3 -m venv .venv

# Activar entorno
source .venv/bin/activate
```

## 4. Dependencias Python (PIP)
Instalar las librerías listadas en `requirements.txt`.

Las principales son:
*   `aiortc`: WebRTC stack (Video y Datos).
*   `aiohttp`: Cliente HTTP y WebSockets asíncrono.
*   `RPi.GPIO`: Control de pines físicos.
*   `python-dotenv`: Carga de configuración.

```bash
pip install -r requirements.txt
```

## 5. Configuración (`.env`)
Crear un archivo `.env` en la raíz con las credenciales entregadas por la plataforma web.

```env
# URL del Backend Central
API_URL=https://tu-plataforma-barco.com

# Token de un solo uso para vincular (Solo primera vez)
BARCO_TOKEN_VINCULACION=XYZ-123

# Credenciales Permanentes (Se generan automáticamnete tras vincular)
NUM_SERIE=VEHICULO-XXX
TOKEN_SECRETO=sk_live_xxx
```

## 6. Ejecución
Para iniciar el cliente en modo producción:

```bash
python main.py
```

El script buscará `rpicam-vid` automáticamente e iniciará la transmisión si el servidor lo solicita.
