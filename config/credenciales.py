import os
import json
import logging
import subprocess
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configuración de logging
logger = logging.getLogger("config.credenciales")

# Ruta al archivo oculto y protegido
# Usamos un archivo punto (.) para que sea oculto en sistemas Unix
RUTA_IDENTIDAD = "config/.barco_identidad_segura"

# Token de Vinculación (Generado en la Web App para asociar el barco)
TOKEN_VINCULACION = os.getenv("BARCO_TOKEN_VINCULACION", "")

def obtener_serial_cpu():
    """
    Intenta obtener el número de serie único del procesador de la Raspberry Pi.
    """
    try:
        # En Raspberry Pi OS, el serial está en /proc/cpuinfo
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    return line.split(':')[1].strip()
    except Exception:
        pass
    
    # Fallback si no estamos en una Pi o no se puede leer
    return "SERIAL-GENERICO-SIMULACION"

def generar_llave_maestra():
    """
    Genera una llave de cifrado vinculada al hardware del dispositivo.
    """
    serial = obtener_serial_cpu()
    sal = b'barco_antigravity_salt' # Sal estática para consistencia
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sal,
        iterations=100000,
    )
    llave = base64.urlsafe_b64encode(kdf.derive(serial.encode()))
    return llave

def guardar_identidad(num_serie, token):
    """
    Cifra y guarda la identidad con permisos restringidos.
    """
    try:
        datos = json.dumps({"num_serie": num_serie, "token": token}).encode()
        fernet = Fernet(generar_llave_maestra())
        datos_cifrados = fernet.encrypt(datos)

        # Escribimos el archivo
        with open(RUTA_IDENTIDAD, "wb") as f:
            f.write(datos_cifrados)
        
        # Aplicamos permisos estrictos: SÓLO EL DUEÑO lee y escribe (chmod 600)
        os.chmod(RUTA_IDENTIDAD, 0o600)
        
        logger.info(f"Identidad cifrada y guardada de forma segura para: {num_serie}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar identidad segura: {e}")
        return False

def obtener_identidad():
    """
    Lee y descifra la identidad local vinculada al hardware.
    """
    if not os.path.exists(RUTA_IDENTIDAD):
        return None
    
    try:
        fernet = Fernet(generar_llave_maestra())
        with open(RUTA_IDENTIDAD, "rb") as f:
            datos_cifrados = f.read()
            
        datos_descifrados = fernet.decrypt(datos_cifrados)
        return json.loads(datos_descifrados.decode())
    except Exception as e:
        logger.error(f"No se pudo descifrar la identidad (¿Cambiastes de hardware?): {e}")
        return None

def eliminar_identidad():
    """
    Elimina los archivos de identidad (reseteo de fábrica).
    """
    if os.path.exists(RUTA_IDENTIDAD):
        os.remove(RUTA_IDENTIDAD)
        logger.info("Identidad segura eliminada satisfactoriamente.")
