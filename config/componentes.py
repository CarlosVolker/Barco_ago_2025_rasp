
"""
ARCHIVO DE CONFIGURACIÓN DEL VEHÍCULO IOT
=========================================

Este archivo define CÓMO está construido tu vehículo físico.
Aquí mapeas los nombres lógicos (ej. "torreta_proa") a los pines físicos (ej. Canal 4 del PCA9685).

INSTRUCCIONES PARA AÑADIR ELEMENTOS:
------------------------------------
1. Identifica qué tipo de componente es:
   - MOTOR: Se mueve rápido y controla velocidad (Brushless/ESC). Agregalo a MOTORES_PROPULSION.
   - SERVO SIMPLE: Se mueve a un ángulo (Dirección, Timón). Agregalo a SERVOS_DIRECCION.
   - MULTI-EJE: Tiene varios servos coordinados (PTZ, Torreta, Brazo). Agregalo a ACTUADORES_MULTIEJE.

2. Copia la estructura del ejemplo y cambia:
   - "nombre": Debe ser único.
   - "canal" / "pin_pwm": Dónde está conectado el cable.
   - "limites" / "angulo_min/max": Ajusta según el rango físico de tu hardware para no romper nada.

"""

# -----------------------------------------------------------------------------
# 1. MOTORES DE PROPULSIÓN (Brushless con ESC)
# -----------------------------------------------------------------------------
# Controlan el avance y retroceso.
# - canal: Número de canal (0-15) en la placa PCA9685.
# - direccion_i2c: Dirección de la placa (0x40 por defecto).

MOTORES_PROPULSION = [
    # Ejemplo Barco: 1 solo motor principal
    {"nombre": "motor_principal", "canal": 12, "direccion_i2c": 0x40},
    
    # Ejemplo Tanque (Descomentar para usar):
    # {"nombre": "oruga_izquierda", "canal": 13, "direccion_i2c": 0x40},
    # {"nombre": "oruga_derecha", "canal": 14, "direccion_i2c": 0x40},
]

# -----------------------------------------------------------------------------
# 2. SERVOS DE DIRECCIÓN / EJES SIMPLES
# -----------------------------------------------------------------------------
# Servos individuales para dirección (autos), timones (barcos) o alerones.
# - canal: Número del 0 al 15 en la placa PCA9685.

SERVOS_DIRECCION = [
    # Ejemplo Barco: Timón central
    {
        "nombre": "timon_central", 
        "canal": 0, 
        "angulo_min": 0,  # Límite izquierdo físico
        "angulo_max": 180,  # Límite derecho físico
        "direccion_i2c": 0x40
    },
]

# -----------------------------------------------------------------------------
# 3. ACTUADORES MULTI-EJE (Complex Systems)
# -----------------------------------------------------------------------------
# Para sistemas que usan más de un servo (Cámaras PTZ, Torretas, Brazos).
# IMPORTANTE: Puedes configurar límites distintos para cada eje.

ACTUADORES_MULTIEJE = [
    # CÁMARA PTZ (Pan-Tilt-Zoom)
    {
        "nombre": "camara_ptz",
        "canales": {
            "pan": 1,   # Servo Horizontal en Canal 1
            "tilt": 2   # Servo Vertical en Canal 2
        },
        "limites": {
            "pan": (0, 180),
            "tilt": (0, 180)
        },
        "direccion_i2c": 0x40
    },

    # TORRETA 1 (Ejemplo de personalización independiente)
    {
        "nombre": "torreta_proa",
        "canales": {"giro": 3, "elevacion": 4},
        "limites": {
            "giro": (0, 180),      
            "elevacion": (0, 180)   
        },
        "pin_accion": 22, # Pin GPIO para activar disparo/láser (Sigue siendo GPIO directo)
        "direccion_i2c": 0x40
    },

    # TORRETA 2 (Ejemplo con límites distintos - Segunda Placa opcional)
    # Si tienes una segunda placa PCA9685, cambia direccion_i2c a 0x41
    {
        "nombre": "torreta_popa",
        "canales": {"giro": 7, "elevacion": 8},
        "limites": {
            "giro": (60, 120),    
            "elevacion": (0, 45)
        },
        "pin_accion": 23,
        "direccion_i2c": 0x40 
    }
]

# -----------------------------------------------------------------------------
# 4. CÁMARAS DE VIDEO
# -----------------------------------------------------------------------------
CAMARAS = [
    {
        "nombre": "frontal",
        "fps": 15,
        "resolucion": (640, 480)
    }
]
