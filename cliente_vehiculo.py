import asyncio
import json
import logging
import os
import time
import random
import platform
import aiohttp
from dotenv import load_dotenv
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
from aiortc.sdp import candidate_from_sdp
from aiortc.contrib.media import MediaPlayer
import websockets
import subprocess

# Importar configuración y controladores genéricos
from config.credenciales import obtener_identidad, guardar_identidad, eliminar_identidad, TOKEN_VINCULACION
from controladores.instancias import motores, servos_direccion, actuadores_multieje
from config.componentes import MOTORES_PROPULSION, SERVOS_DIRECCION, ACTUADORES_MULTIEJE

# Cargar variables de entorno
load_dotenv()

# Configuración de registro (Logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClienteVehiculo")

# Constantes de Red
URL_BACKEND = os.getenv("URL_BACKEND", "https://tu-api-backend.com")
URL_SIGNALING = os.getenv("URL_SIGNALING", "wss://tu-api-backend.com/ws/vehiculo/")
SERVIDOR_STUN = "stun:stun.l.google.com:19302"

class ClienteVehiculo:
    def __init__(self):
        self.pc = None
        self.ws = None
        self.player = None  # Referencia para mantener vivo el reproductor de video
        identidad = obtener_identidad()
        self.num_serie = identidad.get("num_serie") if identidad else None
        self.token = identidad.get("token") if identidad else None
        self.canal_datos = None
        self.ejecutando = True
        self.latencia = 0  # Latencia en ms

    async def registrar_si_es_necesario(self):
        """
        Si no hay identidad local, intenta registrarse en el backend usando el token de vinculación.
        """
        if self.token and self.num_serie:
            logger.info(f"Identidad confirmada: {self.num_serie}")
            return True

        if not TOKEN_VINCULACION:
            logger.error("No se ha configurado el TOKEN_VINCULACION en el .env")
            return False

        logger.info("Solicitando identidad al backend con Token de Vinculación...")
        url = f"{URL_BACKEND}/api/vehiculos/provisionar/"
        
        async with aiohttp.ClientSession() as session:
            try:
                # El vehículo se presenta con el token generado por el usuario en la web
                async with session.post(url, json={"token_vinculacion": TOKEN_VINCULACION}) as resp:
                    if resp.status == 200:
                        datos = await resp.json()
                        self.num_serie = datos.get("num_serie")
                        self.token = datos.get("token_secreto")
                        
                        if self.num_serie and self.token:
                            guardar_identidad(self.num_serie, self.token)
                            logger.info(f"Registro exitoso. Asignado num_serie: {self.num_serie}")
                            return True
                        else:
                            logger.error("El backend no entregó identidad completa.")
                            return False
                    else:
                        logger.error(f"Error en el aprovisionamiento: {resp.status}")
                        return False
            except Exception as e:
                logger.error(f"Error de conexión durante el registro: {e}")
                return False

    async def conectar_signaling(self):
        """
        Establece conexión con el servidor de señalización (Websocket).
        """
        url = f"{URL_SIGNALING}{self.num_serie}/?token={self.token}"
        
        logger.info(f"Conectando a señalización con ID: {self.num_serie}")
        
        while self.ejecutando:
            try:
                async with websockets.connect(url) as websocket:
                    self.ws = websocket
                    logger.info("Conectado al servidor de señalización.")
                    
                    # Notificar al backend que estamos online e informar hardware
                    await self.enviar_señal(None, "inicio_vehiculo", {
                        "num_serie": self.num_serie,
                        "config": {
                            "motores": MOTORES_PROPULSION,
                            "servos_direccion": SERVOS_DIRECCION,
                            "actuadores_multieje": ACTUADORES_MULTIEJE
                        }
                    })

                    # Bucle de recepción de mensajes
                    async for mensaje in websocket:
                        datos = json.loads(mensaje)
                        await self.manejar_mensaje_señalizacion(datos)
            
            except websockets.exceptions.InvalidStatusCode as e:
                if e.status_code in [401, 403]:
                    logger.critical("Acceso denegado (401/403) en WebSocket. Credenciales revocadas.")
                    eliminar_identidad()
                    self.ejecutando = False
                    break
                else:
                     logger.warning(f"Error HTTP en WebSocket: {e.status_code}. Reintentando...")
                     await asyncio.sleep(5)

            except Exception as e:
                logger.warning(f"Conexión de señalización perdida: {e}. Reintentando en 5 segundos...")
                await asyncio.sleep(5)

    async def manejar_mensaje_señalizacion(self, mensaje):
        try:
            tipo = mensaje.get("type")
            remitente = mensaje.get("sender")
            carga = mensaje.get("payload")

            if tipo == "offer":
                if not carga or "sdp" not in carga:
                    logger.error(f"Payload de oferta incompleto o inválido: {carga}")
                    return

                logger.info(f"Recibida oferta WebRTC de {remitente}")
                await self.crear_peer_connection(remitente)
                # Si 'type' no viene en el payload, usamos 'offer' (que es el valor de 'tipo')
                sdp_type = carga.get("type", tipo)
                await self.pc.setRemoteDescription(RTCSessionDescription(sdp=carga["sdp"], type=sdp_type))
                
                respuesta = await self.pc.createAnswer()
                await self.pc.setLocalDescription(respuesta)
                
                await self.enviar_señal(remitente, "answer", {
                    "sdp": self.pc.localDescription.sdp, 
                    "type": self.pc.localDescription.type
                })
            
            elif tipo == "finalizar_conexion":
                logger.info("Solicitud de desconexión recibida. Liberando recursos...")
                await self.liberar_recursos()

            elif tipo == "pong":
                # Calcular latencia
                try:
                    sent_time = float(carga)
                    now = time.time() * 1000
                    self.latencia = now - sent_time
                    logger.debug(f"Latencia actualizada: {self.latencia:.2f} ms")
                except (ValueError, TypeError):
                    logger.warning("Payload de pong inválido")

            elif tipo == "candidate":
                if not carga or "candidate" not in carga or "sdpMid" not in carga or "sdpMLineIndex" not in carga:
                    logger.error(f"Payload de candidato incompleto: {carga}")
                    return

                if self.pc:
                    # Usamos candidate_from_sdp para parsear el string 'candidate:...'
                    candidate_str = carga["candidate"]
                    # Corrección: si el string es solo "candidate:...", aiortc lo parsa.
                    # Pero a veces el string raw puede venir sin el prefijo "candidate:".
                    # El standard dice que el atributo 'candidate' contiene el string completo SDP.
                    
                    try:
                        candidato = candidate_from_sdp(candidate_str)
                        candidato.sdpMid = carga.get("sdpMid")
                        candidato.sdpMLineIndex = carga.get("sdpMLineIndex")
                        await self.pc.addIceCandidate(candidato)
                    except Exception as e_cand:
                        logger.error(f"Error parseando candidato ICE: {e_cand}")
            
            elif tipo == "control":
                # IMPORTANTE: El frontend envía comandos por WS si WebRTC data no está listo
                if carga:
                    # Parseamos si viene como string JSON, si no, usamos el dict directo
                    # A veces la carga ya es el dict
                    self.procesar_comando_control(json.dumps(carga) if isinstance(carga, dict) else carga)

        except Exception as e:
            logger.error(f"Error procesando mensaje de señalización ({tipo}): {e}")

    async def liberar_recursos(self):
        """
        Detiene la cámara, cierra WebRTC y para motores de forma segura.
        """
        # 1. Parar Motores (Seguridad)
        try:
            for motor in motores: 
                motor.detener()
        except: pass
        
        # 2. Cerrar WebRTC
        if self.pc:
            logger.info("Cerrando conexión WebRTC...")
            await self.pc.close()
            self.pc = None

        # 3. Matar proceso de cámara (rpicam-vid)
        # Es crítico matarlo para liberar /dev/video0
        if hasattr(self, 'cam_process') and self.cam_process:
            logger.info("Terminando proceso de cámara...")
            self.cam_process.terminate()
            try:
                self.cam_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                logger.warning("La cámara no se cerró a tiempo, forzando kill...")
                self.cam_process.kill()
            self.cam_process = None
            
        logger.info("Recursos liberados correctamente.")

    async def crear_peer_connection(self, peer_id):
        if self.pc:
            await self.pc.close()

        
        # Servidor STUN por defecto de Google
        servidor_stun = os.getenv("SERVIDOR_STUN", "stun:stun.l.google.com:19302")
        
        # Lista de Servidores ICE (STUN siempre, TURN si está configurado)
        ice_servers = [RTCIceServer(urls=servidor_stun)]
        
        # Verificamos si hay configuración TURN (Crítico para 4G/Entel Chile)
        turn_url = os.getenv("SERVIDOR_TURN_URL")
        turn_user = os.getenv("SERVIDOR_TURN_USER")
        turn_pass = os.getenv("SERVIDOR_TURN_PASS")
        
        if turn_url and turn_user and turn_pass:
            logger.info("Configurando servidor TURN para conexión 4G segura.")
            ice_servers.append(RTCIceServer(
                urls=turn_url,
                username=turn_user,
                credential=turn_pass
            ))

        config_rtc = RTCConfiguration(iceServers=ice_servers)
        self.pc = RTCPeerConnection(configuration=config_rtc)
        
        try:
            # ESTRATEGIA: Uso directo de v4l2 con formato RAW explícito
            # El comando libcamera-vid falló porque MediaPlayer no acepta comandos string directos, solo files.
            # Volvemos al plan de usar FFmpeg nativo con el formato exacto que reportó v4l2-ctl.
            
            if platform.system() == "Linux":
                try:
                    logger.info("Iniciando cámara con estrategia 'rpicam-vid' (Equilibrada 3Mbps + ZeroLatency)...")
                    
                    # Configuración EQUILIBRADA (3 Mbps + Cero Latencia)
                    # Bajamos de 6 a 3 Mbps para evitar bufferbloat (drift).
                    # Subimos GOP a 10 para mejor eficiencia sin sacrificar demasiada latencia de recuperación.
                    cmd = [
                        "rpicam-vid",
                        "-t", "0",
                        "--inline",
                        "--width", "1296",
                        "--height", "972",
                        "--framerate", "25",
                        "--bitrate", "3000000", # 3 Mbps: Punto dulce calidad/latencia
                        "--profile", "high",
                        "--codec", "libav",
                        "--libav-format", "mpegts",
                        "--low-latency", "1",
                        "--g", "10",            # GOP 10
                        "--flush",
                        "-o", "-"
                    ]
                    
                    # Iniciamos el proceso
                    self.cam_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                    
                    # Configuramos MediaPlayer para latencia cero "Fire Hose".
                    # Si FFmpeg se atrasa, descartará frames en vez de encolarlos (max_delay 0).
                    opciones_ffmpeg = {
                        "probesize": "32", 
                        "analyze_duration": "0",
                        "fflags": "nobuffer",
                        "flags": "low_delay",
                        "reorder_queue_size": "0",  # No reordenar frames
                        "max_delay": "0"            # Cero tolerancia al delay
                    }
                    self.player = MediaPlayer(self.cam_process.stdout, format="mpegts", options=opciones_ffmpeg)
                    logger.info("Cámara iniciada vía rpicam-vid (3Mbps Anti-Drift).")

                except Exception as e:
                    logger.error(f"Error al iniciar cámara: {e}")
                    # No relanzamos para que no muera el script, solo avisamos
            else:
                # Windows
                self.player = MediaPlayer("video=Integrated Camera", format="dshow", options={})

            if self.player:
                self.pc.addTrack(self.player.video)
                logger.info("Pista de video añadida.")

        except Exception as e:
            logger.error(f"Error al iniciar cámara: {e}")
            if "No such file" in str(e) and "/dev/video" in str(e):
                logger.warning("Verifique conexión de la cámara. Ejecute 'ls -l /dev/video*' para listar dispositivos.")
            logger.info("Continuando sin video...")

        @self.pc.on("datachannel")
        def on_datachannel(canal):
            logger.info(f"Canal de datos establecido: {canal.label}")
            self.canal_datos = canal
            
            @canal.on("message")
            def on_message(mensaje):
                self.procesar_comando_control(mensaje)

    def procesar_comando_control(self, cmd_json):
        try:
            comando = json.loads(cmd_json)
            tipo = comando.get("tipo")
            
            if tipo == "movimiento":
                velocidad = comando.get("velocidad", 0) # -100 a 100
                giro = comando.get("giro", 90)          # 0 a 180 (para todos los servos de direccion)
                
                # Control de motores
                for motor in motores:
                    motor.establecer_velocidad(velocidad)
                
                # Control de servos de dirección
                for servo in servos_direccion:
                    servo.establecer_angulo(giro)
            
            elif tipo == "motor_individual":
                # Control preciso de un motor específico (útil para tanques o maniobras complejas)
                idx = comando.get("indice", 0)
                velocidad = comando.get("velocidad", 0)
                
                if idx < len(motores):
                    motores[idx].establecer_velocidad(velocidad)
                else:
                    logger.warning(f"Indice de motor {idx} fuera de rango.")
                    
            elif tipo == "actuador_multieje":
                # Formato esperado: {"tipo": "actuador_multieje", "indice": 0, "eje": "pan", "angulo": 90}
                idx = comando.get("indice", 0)
                eje = comando.get("eje")
                angulo = comando.get("angulo")
                accion = comando.get("ejecutar_accion", False)
                
                if idx < len(actuadores_multieje):
                    actuador = actuadores_multieje[idx]
                    if eje is not None and angulo is not None:
                        actuador.mover_eje(eje, angulo)
                    if accion:
                        actuador.ejecutar_accion()

            elif tipo == "parar":
                for motor in motores:
                    motor.establecer_velocidad(0)
                logger.info("PARADA DE EMERGENCIA")

        except Exception as e:
            logger.error(f"Error procesando comando: {e}")

    async def bucle_ping(self):
        """
        Envía pings periódicos para medir latencia.
        """
        while self.ejecutando:
            if self.ws and self.ws.open:
                now = time.time() * 1000  # ms
                try:
                    await self.enviar_señal(None, "ping", now)
                except Exception as e:
                    logger.debug(f"Error enviando ping: {e}")
            
            # Espera aleatoria entre 2 y 5 segundos
            await asyncio.sleep(random.uniform(2, 5))

    def obtener_temperatura_cpu(self):
        """
        Lee la temperatura del CPU desde el sistema de archivos (estándar Linux).
        Devuelve float en grados Celsius.
        """
        try:
            # Método estándar en Raspberry Pi OS
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_raw = f.read().strip()
                return float(temp_raw) / 1000.0
        except Exception:
            # Fallback simulado para Windows o errores
            return 0.0

    async def bucle_telemetria(self):
        """
        Envía parámetros al backend periódicamente.
        """
        url = f"{URL_BACKEND}/api/vehiculos/telemetria/"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        while self.ejecutando:
            if self.token:
                datos_telemetria = {
                    "num_serie": self.num_serie,
                    "estado": "online",
                    "bateria": 12.5,
                    "latitud": -33.4489,
                    "longitud": -70.6693,
                    "intensidad_señal": self.obtener_nivel_senal(),
                    "temperatura_cpu": self.obtener_temperatura_cpu(),
                    "latencia": int(self.latencia)
                }
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, json=datos_telemetria, headers=headers) as resp:
                            if resp.status == 200:
                                pass # Todo OK
                            elif resp.status in [401, 403]:
                                logger.critical(f"Telemetría Rechazada ({resp.status}). Revocando identidad local...")
                                eliminar_identidad()
                                self.ejecutando = False
                                break
                            else:
                                logger.warning(f"Error enviando telemetría: {resp.status}")
                except Exception as e:
                    logger.error(f"Falla en envío de telemetría: {e}")
            
            await asyncio.sleep(10)

    def obtener_nivel_senal(self):
        """
        Obtiene la intensidad de la señal (dBm) desde el sistema.
        Funciona principalmente para Wi-Fi en Linux.
        """
        # Valor por defecto si falla la lectura
        default_dbm = -100

        if platform.system() != "Linux":
            return -70  # Simulación para Windows/Mac

        try:
            # Intento leer /proc/net/wireless (Estándar para Wi-Fi)
            with open("/proc/net/wireless", "r") as f:
                lines = f.readlines()
                # El formato suele tener cabeceras en las 2 primeras líneas
                for line in lines[2:]:
                    parts = line.split()
                    if len(parts) >= 4:
                        # parts[0] es la interfaz (ej: mlan0:)
                        # parts[2] es link quality
                        # parts[3] es level (dBm) - a veces tiene un punto al final (ej: -65.)
                        
                        # Buscamos la interfaz wlan0 o similar
                        if "wlan" in parts[0] or "mlan" in parts[0]:
                            raw_dbm = parts[3].replace(".", "")
                            return int(raw_dbm)
        except Exception:
            pass
            
        # TODO: Implementar lectura para modem celular 4G (AT commands o nmcli)
        # O usar librerías como 'python-networkmanager' si se usa NetworkManager
        return default_dbm

    async def enviar_señal(self, destino, tipo, carga):
        if self.ws:
            await self.ws.send(json.dumps({
                "target": destino,
                "type": tipo,
                "payload": carga
            }))

    async def iniciar(self):
        if await self.registrar_si_es_necesario():
            await asyncio.gather(
                self.conectar_signaling(),
                self.bucle_telemetria(),
                self.bucle_ping()
            )

if __name__ == "__main__":
    cliente = ClienteVehiculo()
    try:
        asyncio.run(cliente.iniciar())
    except KeyboardInterrupt:
        logger.info("Cerrando cliente...")
        cliente.ejecutando = False
