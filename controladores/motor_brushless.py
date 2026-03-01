from controladores.pca9685_manager import GestorPCA9685
import time

class MotorBrushless:
    # Parámetros de ciclo de trabajo para ESCs (estándar 1ms-2ms en 50Hz)
    # Ciclo PWM 5% = 1ms (Mínimo/Reversa)
    # Ciclo PWM 10% = 2ms (Máximo)
    CICLO_MIN = 5.0   
    CICLO_MAX = 10.0  
    
    # CONFIGURACIÓN DE TIPO DE ESC
    # True:  ESC de Dron/Avión (0 es Stop, 100 es Full). Sin reversa.
    # False: ESC de Auto/Barco (0 es Centro/Stop, 100 es Full, -100 es Reversa).
    MODO_UNIDIRECCIONAL = True 

    def __init__(self, nombre, canal, direccion_i2c=0x40):
        """
        Inicializa una instancia del motor brushless usando PCA9685.
        
        Args:
            nombre (str): Identificador del motor.
            canal (int): Canal del PCA9685 (0-15).
            direccion_i2c (int): Dirección de la placa (default 0x40).
        """
        self.nombre = nombre
        self.canal = canal
        self.direccion_i2c = direccion_i2c
        
        # Obtener placa vía Gestor
        self.pca = GestorPCA9685().obtener_placa(direccion_i2c)
        
        # Inicializar en STOP
        self.detener()

    def establecer_velocidad(self, velocidad):
        """
        Establece la velocidad del motor (-100 a 100).
        Automatiza la conversión a pulsos PWM correctos.
        """
        if velocidad < -100: velocidad = -100
        elif velocidad > 100: velocidad = 100

        ciclo_pwm = 0.0
        
        if MotorBrushless.MODO_UNIDIRECCIONAL:
            # MODO UNIDIRECCIONAL (0 a 100) -> 1ms a 2ms
            val_vel = max(0, velocidad) 
            rango_ciclo = MotorBrushless.CICLO_MAX - MotorBrushless.CICLO_MIN
            ciclo_pwm = MotorBrushless.CICLO_MIN + (val_vel / 100.0) * rango_ciclo
            
        else:
            # MODO BIDIRECCIONAL (-100 a 100) -> 1ms a 2ms
            # -100 -> 5% (1ms)
            # 0    -> 7.5% (1.5ms)
            # 100  -> 10% (2ms)
            rango_ciclo = MotorBrushless.CICLO_MAX - MotorBrushless.CICLO_MIN
            ciclo_pwm = MotorBrushless.CICLO_MIN + ((velocidad + 100) / 200.0) * rango_ciclo

        self._aplicar_ciclo(ciclo_pwm)
        # print(f"[Motor {self.nombre}] Velocidad: {velocidad} | PWM: {ciclo_pwm:.2f}%")

    def _aplicar_ciclo(self, ciclo_porcentaje):
        """Aplica el ciclo de trabajo (0-100%) convirtiéndolo a 16-bit integer."""
        duty_cycle_int = int((ciclo_porcentaje / 100.0) * 65535)
        try:
            self.pca.channels[self.canal].duty_cycle = duty_cycle_int
        except Exception as e:
            print(f"[Motor {self.nombre}] Error hardware: {e}")

    def detener(self):
        """Detiene el motor (envía señal de stop)."""
        if MotorBrushless.MODO_UNIDIRECCIONAL:
            self.establecer_velocidad(0)
        else:
            self.establecer_velocidad(0) # En bidireccional 0 es centro/stop

    def calibrar_esc(self):
        """Secuencia de calibración básica."""
        print(f"[Motor {self.nombre}] CALIBRACIÓN: Max...")
        self.establecer_velocidad(100)
        time.sleep(2)
        print(f"[Motor {self.nombre}] CALIBRACIÓN: Min...")
        if MotorBrushless.MODO_UNIDIRECCIONAL:
             self.establecer_velocidad(0)
        else:
             self.establecer_velocidad(-100)
        time.sleep(2)
        print(f"[Motor {self.nombre}] CALIBRACIÓN: Finalizada.")
