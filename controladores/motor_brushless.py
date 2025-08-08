import RPi.GPIO as GPIO
import time



class MotorBrushless:
    _pwm_instances = {}

    # Parámetros de nivel y duty para todos los motores brushless
    NIVEL_MIN = 0
    NIVEL_MAX = 10
    NIVEL_ACTIVO = 5.5  # El motor solo se mueve a partir de este nivel
    DUTY_MIN = 5
    DUTY_MAX = 10

    def __init__(self, nombre, pin_pwm):
        self.nombre = nombre
        self.pin_pwm = pin_pwm
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_pwm, GPIO.OUT)
        if self.pin_pwm not in MotorBrushless._pwm_instances:
            pwm = GPIO.PWM(self.pin_pwm, 50)  # 50 Hz para ESC
            pwm.start(0)
            MotorBrushless._pwm_instances[self.pin_pwm] = pwm
        self.pwm = MotorBrushless._pwm_instances[self.pin_pwm]
        self.nivel = MotorBrushless.NIVEL_MIN

    def subir_nivel(self):
        if self.nivel < MotorBrushless.NIVEL_MAX:
            self.nivel += 1
        self.aplicar_nivel()

    def bajar_nivel(self):
        if self.nivel > MotorBrushless.NIVEL_MIN:
            self.nivel -= 1
        self.aplicar_nivel()

    def set_nivel(self, nivel):
        if nivel < MotorBrushless.NIVEL_MIN:
            nivel = MotorBrushless.NIVEL_MIN
        elif nivel > MotorBrushless.NIVEL_MAX:
            nivel = MotorBrushless.NIVEL_MAX
        self.nivel = nivel
        self.aplicar_nivel()

    def nivel_a_duty(self, nivel=None):
        if nivel is None:
            nivel = self.nivel
        if nivel < MotorBrushless.NIVEL_ACTIVO:
            return MotorBrushless.DUTY_MIN
        # Mapeo lineal de nivel a duty
        duty = MotorBrushless.DUTY_MIN + (MotorBrushless.DUTY_MAX - MotorBrushless.DUTY_MIN) * (nivel - MotorBrushless.NIVEL_ACTIVO) / (MotorBrushless.NIVEL_MAX - MotorBrushless.NIVEL_ACTIVO)
        return min(max(duty, MotorBrushless.DUTY_MIN), MotorBrushless.DUTY_MAX)

    def aplicar_nivel(self):
        duty = self.nivel_a_duty()
        self.pwm.ChangeDutyCycle(duty)
        print(f"[Motor {self.nombre}] Nivel: {self.nivel} | Duty: {duty:.2f}%")

    def inicializar_esc(self, tiempo_espera=2):
        """
        Inicializa el ESC enviando señal de stop (pulso 1500us) durante unos segundos.
        """
        print(f"[Motor {self.nombre}] Inicializando ESC (stop)...")
        self.establecer_velocidad(0)
        time.sleep(tiempo_espera)
        print(f"[Motor {self.nombre}] ESC listo para recibir comandos.")

    def calibrar_esc(self, tiempo_max=2, tiempo_min=2, tiempo_stop=2):
        """
        Calibra el ESC siguiendo la secuencia típica:
        1. Enviar pulso máximo (acelerador a fondo)
        2. Esperar (conectar batería del ESC)
        3. Enviar pulso mínimo (acelerador mínimo)
        4. Esperar
        5. Enviar pulso de stop
        """
        print(f"[Motor {self.nombre}] INICIANDO CALIBRACIÓN ESC")
        print("Coloca el acelerador al máximo (pulso máximo enviado)...")
        self.establecer_velocidad(100)
        time.sleep(tiempo_max)
        print("Ahora coloca el acelerador al mínimo (pulso mínimo enviado)...")
        self.establecer_velocidad(-100)
        time.sleep(tiempo_min)
        print("Enviando pulso de stop...")
        self.establecer_velocidad(0)
        time.sleep(tiempo_stop)
        print(f"[Motor {self.nombre}] CALIBRACIÓN FINALIZADA")

    def detener(self):
        """
        Detiene el motor y libera el PWM del pin.
        """
        print(f"[Motor {self.nombre}] Deteniendo motor y limpiando GPIO...")
        self.establecer_velocidad(0)
        time.sleep(0.5)
        self.pwm.stop()
        GPIO.cleanup(self.pin_pwm)

    def establecer_velocidad(self, velocidad):
        """
        Establece la velocidad y dirección del motor (modo clásico, -100 a 100).
        Si quieres usar niveles, usa set_nivel, subir_nivel o bajar_nivel.
        """
        if velocidad < -100:
            velocidad = -100
        elif velocidad > 100:
            velocidad = 100

        # Mapear -100 a 100 a 1000us a 2000us (1500us es stop)
        pulso_us = int(1500 + (velocidad * 5))
        duty = (pulso_us / 20000) * 100  # 20ms periodo para 50Hz
        self.pwm.ChangeDutyCycle(duty)
        print(f"[Motor {self.nombre}] Velocidad: {velocidad} | PWM: {pulso_us}us | Duty: {duty:.2f}%")
