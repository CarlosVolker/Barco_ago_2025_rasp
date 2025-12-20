
# Controlador Genérico de Vehículos IoT (Raspberry Pi 4)

Este proyecto convierte una **Raspberry Pi 4** en el cerebro de un vehículo controlado por internet (Barco, Auto, Rover, Tanque). Soporta video en tiempo real, telemetría y control de múltiples actuadores (Motores, Servos, PTZ) compatible con redes 4G/NAT.

## Características Principales

*   **Agnóstico al Hardware**: Funciona con cualquier configuración de motores y servos definida en `config/componentes.py`.
*   **Video Baja Latencia**: WebRTC con soporte de HW Acceleration (OpenCV).
*   **Seguridad IoT**: Aprovisionamiento seguro mediante tokens y cifrado de hardware.
*   **Conectividad Universal**: Funciona con cualquier proveedor de Internet (WiFi, 4G, 5G, Starlink) gracias a la autoconfiguración STUN/TURN.
*   **Resiliencia**: Reconexión automática ante caídas de señal.

## Estructura del Proyecto

*   `main.py`: Punto de entrada del sistema.
*   `cliente_vehiculo.py`: Cliente Websocket/WebRTC que se conecta a tu backend.
*   `config/`:
    *   `componentes.py`: **¡EDITA ESTO!** Aquí defines qué motores y servos tienes conectados.
    *   `credenciales.py`: Maneja el cifrado de la identidad del vehículo.
*   `controladores/`: Drivers de hardware (PCA9685, GPIO).
*   `backend_spec.md`: **Guía para Desarrolladores Backend**. Explica cómo construir la API para controlar este cerebro.

## Requisitos de Hardware

1.  Raspberry Pi 4 (Recomendado) o 3B+.
2.  Controlador de Servos **PCA9685** (I2C).
3.  Controlador de Motores (ESC) compatible con PWM.
4.  Cámara USB o Pi Camera.
5.  Conexión a Internet (WiFi o Dongle 4G).

## Instalación y Primer Uso

### 1. Configuración del Sistema
```bash
# Copia el archivo de entorno ejemplo
cp .env.example .env

# EDITA el .env con la URL de tu backend y tu token de vinculación
nano .env
```

### 2. Definición del Hardware
Edita `config/componentes.py` para reflejar tu vehículo real:
*   ¿Cuántos motores tienes?
*   ¿Tienes dirección (servo) o giro diferencial?
*   ¿Tienes cámara PTZ?
```bash
nano config/componentes.py
```

### 3. Instalación de Dependencias
#### 3.1 Librerías del Sistema (Raspberry Pi OS)
```bash
sudo apt update
sudo apt install libvpx-dev libopus-dev libffi-dev libssl-dev libavdevice-dev libavfilter-dev libavformat-dev libavcodec-dev libswscale-dev -y
```

#### 3.2 Librerías Python
```bash
pip install -r requirements.txt
```

#### 3.3 Solución de Problemas Comunes (ImportError: libvpx)
Si recibes errores de librerías (`libvpx`, `libffi`) o de compilación (`av`), fuerza la instalación desde el código fuente para que se adapte a tu Raspberry Pi:

```bash
pip install --upgrade --force-reinstall --no-binary av,aiortc -r requirements.txt
```

### 4. Prueba de Hardware (Opcional)
Antes de conectarte a internet, verifica que tus cables estén bien conectados:
```bash
# Usa las flechas del teclado para mover motores y servos
python test_teclado.py
```

### 5. Ejecución Principal
```bash
python main.py
```
El sistema intentará registrarse en tu backend. Si es la primera vez, usará el `BARCO_TOKEN_VINCULACION` del `.env` para obtener su identidad segura.

## Desarrollo del Backend

Si estás creando el servidor para controlar este vehículo, lee obligatoriamente el archivo:
👉 **[backend_spec.md](backend_spec.md)**

## Documentación Profunda

Para detalles sobre **cifrado, versiones de librerías, protocolos exactos de red y hardware**, consulta:
👉 **[DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md)**
