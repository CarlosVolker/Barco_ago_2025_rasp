
from controladores.pca9685_manager import GestorPCA9685

class ActuadorServo:
    """
    Controlador genérico para un servo utilizando el driver PCA9685.
    Sirve para dirección, timón, o cualquier actuador de un solo eje.
    """

    def __init__(self, nombre, canal, angulo_min, angulo_max, direccion_i2c=0x40):
        """
        Inicializa una instancia de ActuadorServo.
        
        Args:
            nombre (str): Identificador del actuador.
            canal (int): Canal del PCA9685 donde está conectado el servo.
            angulo_min (int): Ángulo mínimo permitido (grados).
            angulo_max (int): Ángulo máximo permitido (grados).
            direccion_i2c (int): Dirección I2C de la placa PCA9685 (default 0x40).
        """
        self.nombre = nombre
        self.canal = canal
        self.angulo_min = angulo_min
        self.angulo_max = angulo_max
        self.direccion_i2c = direccion_i2c
        
        # Obtener referencia a la placa correcta vía el Gestor
        self.pca = GestorPCA9685().obtener_placa(direccion_i2c)

    def establecer_angulo(self, angulo):
        """Establece el ángulo del actuador, limitado por angulo_min y angulo_max"""
        angulo_limitado = max(self.angulo_min, min(self.angulo_max, angulo))
        pulso = self._angulo_a_pwm(angulo_limitado)
        
        try:
            self.pca.channels[self.canal].duty_cycle = pulso
            # print(f"[Actuador {self.nombre}] Ángulo establecido: {angulo_limitado} (PWM: {pulso})")
        except Exception as e:
            print(f"[Actuador {self.nombre}] Error al mover servo: {e}")

    @staticmethod
    def _angulo_a_pwm(angulo):
        # Convierte un ángulo (0-180) a un valor de duty_cycle para PCA9685 (0-0xFFFF)
        min_us = 500   # Pulso mínimo típico en microsegundos
        max_us = 2500  # Pulso máximo típico en microsegundos
        us = min_us + (max_us - min_us) * (angulo / 180.0)
        # PCA9685 duty_cycle: 0-65535 corresponde a 0-20ms (para 50Hz)
        duty_cycle = int((us / 20000.0) * 65535)
        return duty_cycle
