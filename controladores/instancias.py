
from config.componentes import MOTORES_PROPULSION, SERVOS_DIRECCION, ACTUADORES_MULTIEJE
from controladores.motor_brushless import MotorBrushless
from controladores.actuador_servo import ActuadorServo
from controladores.actuador_ejes import ActuadorEjes

# Inicialización genérica de componentes del vehículo

# Motores de propulsión (Brushless)
motores = [MotorBrushless(**m) for m in MOTORES_PROPULSION]

# Servos de dirección o ejes simples
servos_direccion = [ActuadorServo(**s) for s in SERVOS_DIRECCION]

# Actuadores de múltiples ejes (PTZ, Torretas, etc)
actuadores_multieje = [ActuadorEjes(**a) for a in ACTUADORES_MULTIEJE]

# Exportación simplificada para el cliente
__all__ = ["motores", "servos_direccion", "actuadores_multieje"]
