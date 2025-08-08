
# Configuración de pines y cantidad de componentes del barco
# Modifica este archivo para definir la cantidad y pines/canales de cada componente

MOTORES_BRUSHLESS = [
    {"nombre": "motor_izquierdo", "pin_pwm": 17},
    #{"nombre": "motor_central_izquierdo", "pin_pwm": 18},
    #{"nombre": "motor_central_derecho", "pin_pwm": 18},
    #{"nombre": "motor_derecho", "pin_pwm": 18},
]

TIMONES = [
    {"nombre": "timon_principal", "canal": 0, "angulo_min": 30, "angulo_max": 150},
]

TORRETAS = [
    {"nombre": "torreta_1", "canal_giro": 1, "canal_elevacion": 11, "giro_min": 10, "giro_max": 170, "elevacion_min": 20, "elevacion_max": 120},
    {"nombre": "torreta_2", "canal_giro": 2, "canal_elevacion": 14, "giro_min": 0, "giro_max": 180, "elevacion_min": 30, "elevacion_max": 150},
    #{"nombre": "torreta_3", "canal_giro": 3, "canal_elevacion": 15, "giro_min": 15, "giro_max": 165, "elevacion_min": 10, "elevacion_max": 100},
    #{"nombre": "torreta_4", "canal_giro": 4, "canal_elevacion": 16, "giro_min": 5, "giro_max": 175, "elevacion_min": 25, "elevacion_max": 130},
]
