import RPi.GPIO as GPIO
import time




class MotorBrushless:
    _pwm_instances = {}

    # Parámetros de ciclo de trabajo para todos los motores brushless
    CICLO_MIN = 5.0   # Ciclo mínimo (motor quieto o 0 RPM)
    CICLO_MAX = 10.0  # Ciclo máximo (motor máxima velocidad)
    CICLO_INICIO = 0 
    CICLO_PASO = 0.5  
    
    # CONFIGURACIÓN DE TIPO DE ESC
    # True:  ESC de Dron/Avión (0 es Stop, 100 es Full). Sin reversa.
    # False: ESC de Auto/Barco (0 es Centro/Stop, 100 es Full, -100 es Reversa).
    MODO_UNIDIRECCIONAL = True 

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
            
            # Inicializar en MIN (Stop seguro para Unidireccional) o MEDIO (Stop para Bidireccional)
            ciclo_inicial = MotorBrushless.CICLO_MIN 
            if not MotorBrushless.MODO_UNIDIRECCIONAL:
                 # En modo bidireccional, el centro (stop) es el promedio entre min y max
                 ciclo_inicial = (MotorBrushless.CICLO_MIN + MotorBrushless.CICLO_MAX) / 2

            pwm.start(ciclo_inicial)
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
        # ... (Mantener lógica de niveles si es posible, o adaptarla)
        pass # Simplificado por ahora, enfocándonos en establecer_velocidad

    def nivel_a_ciclo(self, nivel=None):
        pass

    def aplicar_nivel(self):
        pass

    def inicializar_esc(self, tiempo_espera=2):
        """
        Inicializa el ESC enviando señal de stop (pulso 1500us o 1000us) durante unos segundos.
        """
        print(f"[Motor {self.nombre}] Inicializando ESC (stop)...")
        self.establecer_velocidad(0)
        time.sleep(tiempo_espera)
        print(f"[Motor {self.nombre}] ESC listo para recibir comandos.")

    def calibrar_esc(self, tiempo_max=2, tiempo_min=2, tiempo_stop=2):
        """
        Calibra el ESC siguiendo la secuencia típica:
        1. Enviar pulso máximo
        2. Esperar
        3. Enviar pulso mínimo
        """
        print(f"[Motor {self.nombre}] INICIANDO CALIBRACIÓN ESC")
        print("Coloca el acelerador al máximo (pulso máximo enviado)...")
        self.establecer_velocidad(100)
        time.sleep(tiempo_max)
        
        print("Ahora coloca el acelerador al mínimo (pulso mínimo enviado)...")
        # En modo unidireccional, 'minimo' es 0 (-100 se clipa a 0)
        # En modo bidireccional, 'minimo' suele ser -100 (reversa full) o 0 (centro)? 
        # Para calibrar, ESCs unidireccionales esperan 0% throttle.
        val_min = -100 if not MotorBrushless.MODO_UNIDIRECCIONAL else 0
        self.establecer_velocidad(val_min)
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
        Establece la velocidad del motor.
        
        MODO BIDIRECCIONAL (Coches/Barcos):
            -100 (Reversa Max) -> 5% Ciclo
             0   (Neutro)      -> 7.5% Ciclo
             100 (Avance Max)  -> 10% Ciclo
             
        MODO UNIDIRECCIONAL (Drones/Aviones):
            -100 a 0 (Stop)    -> 5% Ciclo
             100 (Avance Max)  -> 10% Ciclo
        """
        if velocidad < -100: velocidad = -100
        elif velocidad > 100: velocidad = 100

        ciclo = 0.0
        
        if MotorBrushless.MODO_UNIDIRECCIONAL:
            # MODO UNIDIRECCIONAL (0 a 100)
            # Ignoramos reversa (velocidad negativa = 0)
            val_vel = max(0, velocidad) 
            
            # Mapeo lineal: 0 -> CICLO_MIN, 100 -> CICLO_MAX
            rango_ciclo = MotorBrushless.CICLO_MAX - MotorBrushless.CICLO_MIN
            ciclo = MotorBrushless.CICLO_MIN + (val_vel / 100.0) * rango_ciclo
            
        else:
            # MODO BIDIRECCIONAL (-100 a 100)
            # Mapeo lineal: -100 -> CICLO_MIN, 100 -> CICLO_MAX
            # (velocidad + 100) va de 0 a 200
            rango_ciclo = MotorBrushless.CICLO_MAX - MotorBrushless.CICLO_MIN
            ciclo = MotorBrushless.CICLO_MIN + ((velocidad + 100) / 200.0) * rango_ciclo

        self.pwm.ChangeDutyCycle(ciclo)
        print(f"[Motor {self.nombre}] Velocidad: {velocidad} | Ciclo: {ciclo:.2f}% (Uni: {MotorBrushless.MODO_UNIDIRECCIONAL})")
