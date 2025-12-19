import RPi.GPIO as GPIO
import time




class MotorBrushless:
    _pwm_instances = {}

    # Parámetros de ciclo de trabajo para todos los motores brushless
    CICLO_MIN = 5.0   # Ciclo mínimo (motor quieto)
    CICLO_MAX = 10.0  # Ciclo máximo (motor máxima velocidad)
    CICLO_INICIO = 0 # Ciclo para arrancar suavemente
    CICLO_PASO = 0.5  # Incremento/decremento por cada clic

    def __init__(self, nombre, pin_pwm):
        """
        Inicializa una instancia del motor brushless.
        
        Args:
            nombre (str): Identificador del motor (ej. "motor_izquierdo").
            pin_pwm (int): Pin GPIO (BCM) conectado al ESC del motor.
        """
        self.nombre = nombre
        self.pin_pwm = pin_pwm
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_pwm, GPIO.OUT)
        if self.pin_pwm not in MotorBrushless._pwm_instances:
            pwm = GPIO.PWM(self.pin_pwm, 50)  # 50 Hz para ESC
            pwm.start(MotorBrushless.CICLO_MIN)
            MotorBrushless._pwm_instances[self.pin_pwm] = pwm
        self.pwm = MotorBrushless._pwm_instances[self.pin_pwm]
        self.ciclo_actual = MotorBrushless.CICLO_MIN

    def establecer_ciclo_trabajo(self, ciclo):
        """
        Establece directamente el ciclo de trabajo (duty cycle) del PWM.
        
        Args:
            ciclo (float): Valor del ciclo de trabajo (entre CICLO_MIN y CICLO_MAX).
        """
        # Limita el ciclo al rango permitido
        ciclo = max(MotorBrushless.CICLO_MIN, min(MotorBrushless.CICLO_MAX, ciclo))
        self.ciclo_actual = ciclo
        self.pwm.ChangeDutyCycle(ciclo)
        print(f"[Motor {self.nombre}] Ciclo aplicado: {ciclo:.2f}%")

    def subir_ciclo(self):
        """Incrementa el ciclo de trabajo en un paso predefinido (CICLO_PASO)."""
        nuevo_ciclo = self.ciclo_actual + MotorBrushless.CICLO_PASO
        self.establecer_ciclo_trabajo(nuevo_ciclo)
        print(f"[Motor {self.nombre}] Ciclo aumentado a: {self.ciclo_actual:.2f}%")

    def bajar_ciclo(self):
        """Decrementa el ciclo de trabajo en un paso predefinido (CICLO_PASO)."""
        nuevo_ciclo = self.ciclo_actual - MotorBrushless.CICLO_PASO
        self.establecer_ciclo_trabajo(nuevo_ciclo)
        print(f"[Motor {self.nombre}] Ciclo disminuido a: {self.ciclo_actual:.2f}%")


    def subir_nivel(self):
        """Sube un nivel de velocidad discreto."""
        if self.nivel < MotorBrushless.NIVEL_MAX:
            self.nivel += 1
        self.aplicar_nivel()

    def bajar_nivel(self):
        """Baja un nivel de velocidad discreto."""
        if self.nivel > MotorBrushless.NIVEL_MIN:
            self.nivel -= 1
        self.aplicar_nivel()

    def establecer_nivel(self, nivel):
        """
        Establece un nivel de velocidad específico.
        
        Args:
            nivel (int): Nivel deseado (entre NIVEL_MIN e NIVEL_MAX).
        """
        if nivel < MotorBrushless.NIVEL_MIN:
            nivel = MotorBrushless.NIVEL_MIN
        elif nivel > MotorBrushless.NIVEL_MAX:
            nivel = MotorBrushless.NIVEL_MAX
        self.nivel = nivel
        self.aplicar_nivel()

    def nivel_a_ciclo(self, nivel=None):
        """
        Convierte un nivel discreto a un valor de ciclo de trabajo.
        
        Args:
            nivel (int, optional): Nivel a convertir. Si es None, usa el nivel actual.
            
        Returns:
            float: Valor de ciclo de trabajo correspondiente.
        """
        if nivel is None:
            nivel = self.nivel
        # Mapeo lineal de nivel a ciclo (0 a 10)
        ciclo = MotorBrushless.CICLO_MIN + (MotorBrushless.CICLO_MAX - MotorBrushless.CICLO_MIN) * (nivel / (MotorBrushless.NIVEL_MAX - MotorBrushless.NIVEL_MIN))
        return min(max(ciclo, MotorBrushless.CICLO_MIN), MotorBrushless.CICLO_MAX)

    def aplicar_nivel(self):
        """Aplica el ciclo de trabajo correspondiente al nivel actual."""
        ciclo = self.nivel_a_ciclo()
        self.pwm.ChangeDutyCycle(ciclo)
        print(f"[Motor {self.nombre}] Nivel: {self.nivel} | Ciclo: {ciclo:.2f}%")

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
        Ahora velocidad 0 corresponde a 5% de ciclo (CICLO_MIN), y 100 a CICLO_MAX.
        """
        if velocidad < -100:
            velocidad = -100
        elif velocidad > 100:
            velocidad = 100

        # Mapear -100 a 100 a CICLO_MIN a CICLO_MAX
        ciclo = MotorBrushless.CICLO_MIN + ((velocidad + 100) / 200) * (MotorBrushless.CICLO_MAX - MotorBrushless.CICLO_MIN)
        self.pwm.ChangeDutyCycle(ciclo)
        print(f"[Motor {self.nombre}] Velocidad: {velocidad} | Ciclo: {ciclo:.2f}%")
