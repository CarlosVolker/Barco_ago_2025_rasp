

import board
import busio
from adafruit_pca9685 import PCA9685


class Torreta:
    # Compartir el bus y el controlador PCA9685 entre todas las instancias
    _i2c = None
    _pca = None

    def __init__(self, nombre, canal_giro, canal_elevacion, giro_min, giro_max, elevacion_min, elevacion_max):
        self.nombre = nombre
        self.canal_giro = canal_giro
        self.canal_elevacion = canal_elevacion
        self.giro_min = giro_min
        self.giro_max = giro_max
        self.elevacion_min = elevacion_min
        self.elevacion_max = elevacion_max
        # Inicialización real del bus I2C y PCA9685 (solo una vez)
        if Torreta._i2c is None:
            Torreta._i2c = busio.I2C(board.SCL, board.SDA)
        if Torreta._pca is None:
            Torreta._pca = PCA9685(Torreta._i2c)
            Torreta._pca.frequency = 50  # Frecuencia típica para servos

    def girar(self, angulo):
        """Gira la torreta al ángulo especificado, limitado por giro_min y giro_max"""
        angulo_limitado = max(self.giro_min, min(self.giro_max, angulo))
        pulso = self._angulo_a_pwm(angulo_limitado)
        Torreta._pca.channels[self.canal_giro].duty_cycle = pulso
        print(f"[Torreta {self.nombre}] Giro a: {angulo_limitado} (PWM: {pulso})")

    def elevar(self, angulo):
        """Eleva el cañón de la torreta al ángulo especificado, limitado por elevacion_min y elevacion_max"""
        angulo_limitado = max(self.elevacion_min, min(self.elevacion_max, angulo))
        pulso = self._angulo_a_pwm(angulo_limitado)
        Torreta._pca.channels[self.canal_elevacion].duty_cycle = pulso
        print(f"[Torreta {self.nombre}] Elevación a: {angulo_limitado} (PWM: {pulso})")

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
