
from controladores.pca9685_manager import GestorPCA9685

class ActuadorEjes:
    """
    Controlador genérico para un sistema de múltiples ejes (servos).
    Sirve para Torretas, Cámaras PTZ, Brazos Robóticos, etc.
    """

    def __init__(self, nombre, canales, limites, pin_accion=None, direccion_i2c=0x40):
        """
        Inicializa una instancia de ActuadorEjes.
        
        Args:
            nombre (str): Identificador del actuador (ej. "torreta_1", "camara_ptz").
            canales (dict): Mapeo de ejes a canales PCA9685 (ej. {"pan": 0, "tilt": 1}).
            limites (dict): Mapeo de ejes a tuplas (min, max) de ángulos.
            pin_accion (int): Opcional. Pin GPIO para una acción extra (ej. disparar, foto).
            direccion_i2c (int): Dirección I2C de la placa PCA9685 (default 0x40).
        """
        self.nombre = nombre
        self.canales = canales
        self.limites = limites
        self.pin_accion = pin_accion
        self.direccion_i2c = direccion_i2c
        
        # Obtener referencia a la placa correcta vía el Gestor
        self.pca = GestorPCA9685().obtener_placa(self.direccion_i2c)

    def mover_eje(self, eje, angulo):
        """Mueve un eje específico al ángulo deseado, respetando límites."""
        if eje not in self.canales:
            print(f"[Actuador {self.nombre}] Error: Eje {eje} no configurado.")
            return

        min_ang, max_ang = self.limites.get(eje, (0, 180))
        angulo_limitado = max(min_ang, min(max_ang, angulo))
        
        pulso = self._angulo_a_pwm(angulo_limitado)
        
        try:
            self.pca.channels[self.canales[eje]].duty_cycle = pulso
            # print(f"[Actuador {self.nombre}] Eje {eje} movido a: {angulo_limitado}")
        except Exception as e:
            print(f"[Actuador {self.nombre}] Error moviendo eje {eje}: {e}")

    def ejecutar_accion(self):
        """Ejecuta la acción principal del actuador (disparar, capturar, etc)."""
        if self.pin_accion:
            print(f"[Actuador {self.nombre}] Ejecutando acción en pin {self.pin_accion}...")
            # Lógica de hardware aquí (Probablemente GPIO directo, no PCA)
            # Si se requiere GPIO, se debe importar RPi.GPIO aquí o pasar una función de callback
        else:
            print(f"[Actuador {self.nombre}] Acción ejecutada (Simulada).")

    @staticmethod
    def _angulo_a_pwm(angulo):
        min_us = 500
        max_us = 2500
        us = min_us + (max_us - min_us) * (angulo / 180.0)
        duty_cycle = int((us / 20000.0) * 65535)
        return duty_cycle
