
import pigpio

class MotorBrushless:
    # Compartir la instancia de pigpio entre todos los motores
    _pi = None

    def __init__(self, nombre, pin_pwm):
        self.nombre = nombre
        self.pin_pwm = pin_pwm
        # Inicialización real de pigpio (solo una vez)
        if MotorBrushless._pi is None:
            MotorBrushless._pi = pigpio.pi()
        # Configurar el pin como salida PWM
        MotorBrushless._pi.set_mode(self.pin_pwm, pigpio.OUTPUT)

    def establecer_velocidad(self, velocidad):
        """
        Establece la velocidad y dirección del motor.
        velocidad: int o float en el rango -100 (máxima reversa) a 100 (máxima adelante), 0 es parado.
        """
        if velocidad < -100:
            velocidad = -100
        elif velocidad > 100:
            velocidad = 100

        # Mapear -100 a 100 a 1000us a 2000us (1500us es stop)
        pulso_us = int(1500 + (velocidad * 5))
        # Enviar pulso PWM real al ESC usando pigpio
        MotorBrushless._pi.set_servo_pulsewidth(self.pin_pwm, pulso_us)
        print(f"[Motor {self.nombre}] Velocidad: {velocidad} | PWM: {pulso_us}us")
