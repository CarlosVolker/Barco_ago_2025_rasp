
import board
import busio
from adafruit_pca9685 import PCA9685


class Timon:
    # Compartir el bus y el controlador PCA9685 entre todas las instancias
    _i2c = None
    _pca = None

    def __init__(self, nombre, canal, angulo_min, angulo_max):
        self.nombre = nombre
        self.canal = canal
        self.angulo_min = angulo_min
        self.angulo_max = angulo_max
        # Inicialización real del bus I2C y PCA9685 (solo una vez)
        if Timon._i2c is None:
            Timon._i2c = busio.I2C(board.SCL, board.SDA)
        if Timon._pca is None:
            Timon._pca = PCA9685(Timon._i2c)
            Timon._pca.frequency = 50  # Frecuencia típica para servos

    def establecer_angulo(self, angulo):
        """Establece el ángulo del timón, limitado por angulo_min y angulo_max"""
        angulo_limitado = max(self.angulo_min, min(self.angulo_max, angulo))
        pulso = self._angulo_a_pwm(angulo_limitado)
        Timon._pca.channels[self.canal].duty_cycle = pulso
        print(f"[Timón {self.nombre}] Ángulo establecido: {angulo_limitado} (PWM: {pulso})")

    @staticmethod
    def _angulo_a_pwm(angulo):
        # Convierte un ángulo (0-180) a un valor de duty_cycle para PCA9685 (0-0xFFFF)
        # Ajusta los valores según tu servo si es necesario
        min_us = 500   # Pulso mínimo típico en microsegundos
        max_us = 2500  # Pulso máximo típico en microsegundos
        us = min_us + (max_us - min_us) * (angulo / 180)
        # PCA9685 duty_cycle: 0-65535 corresponde a 0-20ms (para 50Hz)
        duty_cycle = int((us / 20000) * 65535)
        return duty_cycle
