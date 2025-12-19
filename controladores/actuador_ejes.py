
import board
import busio
from adafruit_pca9685 import PCA9685


class ActuadorEjes:
    """
    Controlador genérico para un sistema de múltiples ejes (servos).
    Sirve para Torretas, Cámaras PTZ, Brazos Robóticos, etc.
    """
    # Compartir el bus y el controlador PCA9685 entre todas las instancias
    _i2c = None
    _pca = None

    def __init__(self, nombre, canales, limites, pin_accion=None):
        """
        Inicializa una instancia de ActuadorEjes.
        
        Args:
            nombre (str): Identificador del actuador (ej. "torreta_1", "camara_ptz").
            canales (dict): Mapeo de ejes a canales PCA9685 (ej. {"pan": 0, "tilt": 1}).
            limites (dict): Mapeo de ejes a tuplas (min, max) de ángulos.
            pin_accion (int): Opcional. Pin GPIO para una acción extra (ej. disparar, foto).
        """
        self.nombre = nombre
        self.canales = canales
        self.limites = limites
        self.pin_accion = pin_accion
        
        # Inicialización real del bus I2C y PCA9685 (solo una vez)
        if ActuadorEjes._i2c is None:
            ActuadorEjes._i2c = busio.I2C(board.SCL, board.SDA)
        if ActuadorEjes._pca is None:
            ActuadorEjes._pca = PCA9685(ActuadorEjes._i2c)
            ActuadorEjes._pca.frequency = 50 

    def mover_eje(self, eje, angulo):
        """Mueve un eje específico al ángulo deseado, respetando límites."""
        if eje not in self.canales:
            print(f"[Actuador {self.nombre}] Error: Eje {eje} no configurado.")
            return

        min_ang, max_ang = self.limites.get(eje, (0, 180))
        angulo_limitado = max(min_ang, min(max_ang, angulo))
        
        pulso = self._angulo_a_pwm(angulo_limitado)
        ActuadorEjes._pca.channels[self.canales[eje]].duty_cycle = pulso
        print(f"[Actuador {self.nombre}] Eje {eje} movido a: {angulo_limitado}")

    def ejecutar_accion(self):
        """Ejecuta la acción principal del actuador (disparar, capturar, etc)."""
        if self.pin_accion:
            print(f"[Actuador {self.nombre}] Ejecutando acción en pin {self.pin_accion}...")
            # Lógica de hardware aquí
        else:
            print(f"[Actuador {self.nombre}] Acción ejecutada (Simulada).")

    @staticmethod
    def _angulo_a_pwm(angulo):
        min_us = 500
        max_us = 2500
        us = min_us + (max_us - min_us) * (angulo / 180)
        duty_cycle = int((us / 20000) * 65535)
        return duty_cycle
