
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
# - pin_pwm: Número de pin GPIO (BCM) de la Raspberry Pi.

MOTORES_PROPULSION = [
    # Ejemplo Barco: 1 solo motor principal
    {"nombre": "motor_principal", "pin_pwm": 17},
    
    # Ejemplo Tanque (Descomentar para usar):
    # {"nombre": "oruga_izquierda", "pin_pwm": 18},
    # {"nombre": "oruga_derecha", "pin_pwm": 19},
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
        "angulo_max": 180  # Límite derecho físico
    },
    
    # Ejemplo Auto (Descomentar):
    # {
    #     "nombre": "direccion_delantera", 
    #     "canal": 0, 
    #     "angulo_min": 60, 
    #     "angulo_max": 120
    # },
]

# -----------------------------------------------------------------------------
# 3. ACTUADORES MULTI-EJE (Complex Systems)
# -----------------------------------------------------------------------------
# Para sistemas que usan más de un servo (Cámaras PTZ, Torretas, Brazos).
# IMPORTANTE: Puedes configurar límites distintos para cada eje.

ACTUADORES_MULTIEJE = [
    # CÁMARA PTZ (Pan-Tilt-Zoom)
    # Ejemplo solicitado: PTZ de 2 servos (Horizontal y Vertical).
    # Si tuvieras 3 (Zoom/Roll), solo añade "roll": canal en el diccionario.
    {
        "nombre": "camara_ptz",
        "canales": {
            "pan": 1,   # Servo Horizontal en Canal 1
            "tilt": 2   # Servo Vertical en Canal 2
        },
        "limites": {
            # El eje horizontal suele tener más recorrido (ej. 0 a 180 grados)
            "pan": (0, 180),
            # El eje vertical suele estar más restringido (ej. 45 a 90 grados) para no mirar el techo
            "tilt": (0, 180)
        }
    },

    # TORRETA 1 (Ejemplo de personalización independiente)
    {
        "nombre": "torreta_proa",
        "canales": {"giro": 3, "elevacion": 4},
        "limites": {
            "giro": (0, 180),      # Esta torreta gira completo
            "elevacion": (0, 180)   # Solo eleva un poco
        },
        "pin_accion": 22 # Pin GPIO para activar disparo/láser
    },

    # TORRETA 2 (Ejemplo con límites distintos)
    # Esta torreta podría estar bloqueada por una estructura, así que limitamos su giro.
    {
        "nombre": "torreta_popa",
        "canales": {"giro": 7, "elevacion": 8},
        "limites": {
            "giro": (60, 120),     # GIRO RESTRINGIDO
            "elevacion": (0, 45)
        },
        "pin_accion": 23
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
