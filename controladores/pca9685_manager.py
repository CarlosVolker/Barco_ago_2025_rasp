try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
    HARDWARE_DISPONIBLE = True
except Exception:
    HARDWARE_DISPONIBLE = False
    print("[GestorPCA] Librerías de hardware no encontradas. Modo SIMULACIÓN activado.")

class GestorPCA9685:
    _instancia = None
    _i2c = None
    _placas = {}

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(GestorPCA9685, cls).__new__(cls)
            
            if HARDWARE_DISPONIBLE:
                try:
                    cls._i2c = busio.I2C(board.SCL, board.SDA)
                except Exception as e:
                    print(f"[GestorPCA] Error inicializando I2C: {e}")
                    cls._i2c = None 
            else:
                cls._i2c = None

        return cls._instancia

    def obtener_placa(self, direccion=0x40):
        """
        Devuelve la instancia de PCA9685 para la dirección I2C dada.
        Si no existe, la crea.
        """
        if self._i2c is None:
            # Si no hay I2C (por error o por falta de libs), devolvemos Mock
            return MockPCA()

        if direccion not in self._placas:
            try:
                pca = PCA9685(self._i2c, address=direccion)
                pca.frequency = 50
                self._placas[direccion] = pca
                print(f"[GestorPCA] Placa conectada en 0x{direccion:X}")
            except Exception as e:
                print(f"[GestorPCA] Error conectando placa 0x{direccion:X}: {e}")
                return MockPCA()
        
        return self._placas[direccion]


class MockChannel:
    duty_cycle = 0

class MockPCA:
    """Simulador para cuando no hay hardware I2C real"""
    def __init__(self):
        self.channels = [MockChannel() for _ in range(16)]
        self.frequency = 50
