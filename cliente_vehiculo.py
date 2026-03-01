import asyncio
import json
import logging
import time
import random
import platform
import aiohttp
from dotenv import load_dotenv
from aiortc import RTCSessionDescription, RTCIceCandidate, RTCPeerConnection
from aiortc.sdp import candidate_from_sdp
import websockets

# Importar configuración y controladores genéricos
from config.credenciales import obtener_identidad, guardar_identidad, eliminar_identidad, TOKEN_VINCULACION
from src.edge_agent.bootstrap.settings import get_settings
from src.edge_agent.control import ControlRuntime
from src.edge_agent.contracts.signaling import SignalEnvelope
from src.edge_agent.observability import MetricsCollector
from src.edge_agent.runtime.legacy_adapter import build_inicio_payload, build_telemetry_payload
from src.edge_agent.safety import DeadmanTimer
from src.edge_agent.video import VideoPipeline
from src.edge_agent.webrtc import PeerManager

# Cargar variables de entorno
load_dotenv()

# Configuración de registro (Logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClienteVehiculo")

class ClienteVehiculo:
    def __init__(self):
        self.settings = get_settings()
        self.pc: RTCPeerConnection | None = None
        self.ws = None
        self.player = None  # Referencia para mantener vivo el reproductor de video
        identidad = obtener_identidad()
        self.num_serie = identidad.get("num_serie") if identidad else None
        self.token = identidad.get("token") if identidad else None
        self.canal_datos = None
        self.ejecutando = True
        self.latencia = 0  # Latencia en ms
        self.control_runtime = ControlRuntime()
        self.video_pipeline = VideoPipeline(profile=self.settings.video_profile)
        self.peer_manager = PeerManager(self.video_pipeline)
        self.metrics = MetricsCollector()
        self.deadman = DeadmanTimer(self.settings.control_deadman_ms, self._on_deadman_timeout)
        self.http_session: aiohttp.ClientSession | None = None

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
        url = f"{self.settings.url_backend}/api/vehiculos/provisionar/"

        session = self.http_session
        created_session = False
        if session is None:
            timeout = aiohttp.ClientTimeout(total=self.settings.telemetry_request_timeout_s)
            session = aiohttp.ClientSession(timeout=timeout)
            created_session = True

        try:
            # El vehículo se presenta con el token generado por el usuario en la web
            async with session.post(url, json={"token_vinculacion": TOKEN_VINCULACION}) as resp:
                if resp.status == 200:
                    datos = await resp.json()
                    self.num_serie = datos.get("num_serie")
                    self.token = datos.get("token_secreto")

                    if self.num_serie and self.token:
                        guardar_identidad(self.num_serie, self.token)
                        self.metrics.inc("provision_success")
                        logger.info(f"Registro exitoso. Asignado num_serie: {self.num_serie}")
                        return True

                    logger.error("El backend no entregó identidad completa.")
                    self.metrics.inc("provision_invalid_payload")
                    return False

                logger.error(f"Error en el aprovisionamiento: {resp.status}")
                self.metrics.inc("provision_error_status")
                return False
        except Exception as e:
            self.metrics.inc("provision_connection_error")
            logger.error(f"Error de conexión durante el registro: {e}")
            return False
        finally:
            if created_session:
                await session.close()

    async def conectar_signaling(self):
        """
        Establece conexión con el servidor de señalización (Websocket).
        """
        url = f"{self.settings.url_signaling}{self.num_serie}/?token={self.token}"
        retry_delay_s = 1.0
        max_delay_s = 30.0
        
        logger.info(f"Conectando a señalización con ID: {self.num_serie}")
        
        while self.ejecutando:
            should_retry = True
            try:
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                ) as websocket:
                    self.ws = websocket
                    retry_delay_s = 1.0
                    self.metrics.inc("signaling_connections")
                    logger.info("Conectado al servidor de señalización.")
                    
                    # Notificar al backend que estamos online e informar hardware
                    await self.enviar_señal(None, "inicio_vehiculo", build_inicio_payload(str(self.num_serie or "")))

                    # Bucle de recepción de mensajes
                    async for mensaje in websocket:
                        datos = json.loads(mensaje)
                        await self.manejar_mensaje_señalizacion(datos)
            
            except websockets.exceptions.InvalidStatusCode as e:
                if e.status_code in [401, 403]:
                    logger.critical("Acceso denegado (401/403) en WebSocket. Credenciales revocadas.")
                    eliminar_identidad()
                    self.ejecutando = False
                    should_retry = False
                else:
                    self.metrics.inc("signaling_http_errors")
                    logger.warning(f"Error HTTP en WebSocket: {e.status_code}.")

            except Exception as e:
                self.metrics.inc("signaling_disconnects")
                logger.warning(f"Conexión de señalización perdida: {e}.")
            finally:
                self.ws = None

            if not self.ejecutando or not should_retry:
                break

            wait_s = min(max_delay_s, retry_delay_s + random.uniform(0, retry_delay_s * 0.2))
            logger.info("Reintentando señalización en %.2f segundos...", wait_s)
            self.metrics.set_gauge("signaling_retry_delay_s", wait_s)
            await asyncio.sleep(wait_s)
            retry_delay_s = min(max_delay_s, retry_delay_s * 2)

    async def manejar_mensaje_señalizacion(self, mensaje):
        tipo = "desconocido"
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
                if self.pc is None:
                    logger.error("No se pudo crear RTCPeerConnection.")
                    return
                pc = self.pc
                # Si 'type' no viene en el payload, usamos 'offer' (que es el valor de 'tipo')
                sdp_type = carga.get("type", tipo)
                await pc.setRemoteDescription(RTCSessionDescription(sdp=carga["sdp"], type=sdp_type))
                
                respuesta = await pc.createAnswer()
                await pc.setLocalDescription(respuesta)
                
                await self.enviar_señal(remitente, "answer", {
                    "sdp": pc.localDescription.sdp,
                    "type": pc.localDescription.type
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
                    self.metrics.set_gauge("latency_ms", self.latencia)
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
            logger.error(f"Error procesando mensaje de señalización: {e}")

    async def liberar_recursos(self):
        """
        Detiene la cámara, cierra WebRTC y para motores de forma segura.
        """
        self.deadman.stop()

        # 1. Motores a Neutro (Standby)
        self.control_runtime.stop_all_motors()
        
        # 2. Detener pipeline de video
        self.video_pipeline.stop()

        # 3. Cerrar WebRTC
        if self.pc:
            logger.info("Cerrando conexión WebRTC...")
            await self.pc.close()
            self.pc = None
            
        logger.info("Recursos liberados correctamente.")

    async def crear_peer_connection(self, peer_id):
        if self.pc:
            await self.pc.close()

        def on_datachannel_ready(canal):
            self.canal_datos = canal

        self.pc = self.peer_manager.create_peer(
            on_data_message=self.procesar_comando_control,
            on_datachannel_ready=on_datachannel_ready,
        )
        self.deadman.start()
        self.metrics.inc("peer_connections_created")
        self.metrics.set_gauge("video_profile", {"low": 0, "balanced": 1, "high": 2}.get(self.video_pipeline.profile, 1))

    def procesar_comando_control(self, cmd_json):
        if self.control_runtime.process_command(cmd_json):
            self.deadman.touch()
            self.metrics.inc("control_commands_ok")
            return

        self.metrics.inc("control_commands_invalid")

    async def _on_deadman_timeout(self):
        logger.warning("Deadman timeout alcanzado, deteniendo motores por seguridad.")
        self.metrics.inc("deadman_timeouts")
        self.control_runtime.stop_all_motors()

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

    async def bucle_observabilidad(self):
        interval = max(5, self.settings.observability_log_interval_s)
        while self.ejecutando:
            snapshot = self.metrics.snapshot()
            counters = snapshot.get("counters", {})
            gauges = snapshot.get("gauges", {})
            logger.info(
                "Observability snapshot | counters=%s gauges=%s",
                counters,
                gauges,
            )
            await asyncio.sleep(interval)

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
        url = f"{self.settings.url_backend}/api/vehiculos/telemetria/"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        while self.ejecutando:
            if self.token:
                datos_telemetria = build_telemetry_payload(
                    num_serie=self.num_serie,
                    estado="online",
                    bateria=12.5,
                    latitud=-33.4489,
                    longitud=-70.6693,
                    intensidad_señal=self.obtener_nivel_senal(),
                    temperatura_cpu=self.obtener_temperatura_cpu(),
                    latencia=int(self.latencia),
                )
                
                try:
                    session = self.http_session
                    if session is None:
                        logger.warning("Sesion HTTP no disponible para telemetria.")
                        self.metrics.inc("telemetry_session_missing")
                    else:
                        async with session.post(url, json=datos_telemetria, headers=headers) as resp:
                            if resp.status == 200:
                                self.metrics.inc("telemetry_sent")
                            elif resp.status in [401, 403]:
                                logger.critical(f"Telemetría Rechazada ({resp.status}). Revocando identidad local...")
                                self.metrics.inc("telemetry_rejected")
                                eliminar_identidad()
                                self.ejecutando = False
                                break
                            else:
                                self.metrics.inc("telemetry_error_status")
                                logger.warning(f"Error enviando telemetría: {resp.status}")
                except Exception as e:
                    self.metrics.inc("telemetry_exception")
                    logger.error(f"Falla en envío de telemetría: {e}")
            
            await asyncio.sleep(self.settings.telemetry_interval_s)

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
            envelope = SignalEnvelope(target=destino, type=tipo, payload=carga)
            await self.ws.send(envelope.model_dump_json())

    async def iniciar(self):
        if self.http_session is None:
            timeout = aiohttp.ClientTimeout(total=self.settings.telemetry_request_timeout_s)
            self.http_session = aiohttp.ClientSession(timeout=timeout)

        try:
            if await self.registrar_si_es_necesario():
                await asyncio.gather(
                    self.conectar_signaling(),
                    self.bucle_telemetria(),
                    self.bucle_ping(),
                    self.bucle_observabilidad(),
                )
        finally:
            self.deadman.stop()
            if self.http_session is not None:
                await self.http_session.close()
                self.http_session = None

if __name__ == "__main__":
    cliente = ClienteVehiculo()
    try:
        asyncio.run(cliente.iniciar())
    except KeyboardInterrupt:
        logger.info("Cerrando cliente...")
        cliente.ejecutando = False
