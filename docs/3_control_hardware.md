# Documentación: Control de Hardware y Motores

El sistema abstrae el hardware físico mediante controladores modulares en Python, permitiendo cambiar componentes sin reescribir la lógica de red.

## Configuración de Pines
El mapeo de pines GPIO (BCM) y canales PWM se define exclusivamente en:
`config/componentes.py`
Edite ese archivo para asignar motores, servos y actuadores a los pines correspondientes de su Raspberry Pi o placa PCA9685.

## Controlador de Motores Brushless (`MotorBrushless`)

Clase ubicada en `controladores/motor_brushless.py`. Maneja Electronic Speed Controllers (ESC) estándar mediante PWM.

### Principio de Funcionamiento
Los ESC estándar de modelismo esperan una señal PWM de 50Hz. La velocidad se controla mediante el ancho del pulso positivo (Duty Cycle).

*   **Frecuencia**: 50 Hz (Estándar Servo/ESC).
*   **Ciclo Mínimo (Stop/Reversa Max)**: ~5% (1ms).
*   **Ciclo Máximo (Adelante Max)**: ~10% (2ms).
*   **Mapeo**: El software convierte una entrada de velocidad de **-100 a 100** a este rango de ciclo de trabajo PWM.

### Funciones Principales

*   `establecer_velocidad(velocidad)`: Recibe un entero entre -100 y 100. Interpola linealmente al ciclo de trabajo correspondiente.
*   `calibrar_esc()`: Ejecuta la secuencia de seguridad para "enseñarle" al ESC los límites máximos y mínimos (necesario si se cambia el ESC).
*   `detener()`: Envía señal 0 y libera los recursos GPIO para seguridad.

## Seguridad y Failsafe

### 1. Watchdog de Conexión
El cliente (`cliente_vehiculo.py`) monitorea la conexión WebRTC.
*   **Evento**: Si la conexión WebRTC se cierra o falla ("failed", "closed").
*   **Acción**: Se llama inmediatamente a `detener_todo()`, poniendo todos los motores en 0.

### 2. Inicialización Segura
Al arrancar el script, los motores se inicializan en estado neutro (Stop) durante 2 segundos para evitar giros bruscos si el ESC estaba encendido antes que la Pi.
