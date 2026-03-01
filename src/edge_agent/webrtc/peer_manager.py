import logging
import os

from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection

from src.edge_agent.video.pipeline import VideoPipeline

logger = logging.getLogger("edge_agent.webrtc.peer_manager")


class PeerManager:
    def __init__(self, video_pipeline: VideoPipeline | None = None):
        self.video_pipeline = video_pipeline or VideoPipeline()

    def _build_rtc_configuration(self) -> RTCConfiguration:
        servidor_stun = os.getenv("SERVIDOR_STUN", "stun:stun.l.google.com:19302")
        ice_servers = [RTCIceServer(urls=servidor_stun)]

        turn_url = os.getenv("SERVIDOR_TURN_URL")
        turn_user = os.getenv("SERVIDOR_TURN_USER")
        turn_pass = os.getenv("SERVIDOR_TURN_PASS")
        if turn_url and turn_user and turn_pass:
            logger.info("Configurando servidor TURN para conectividad restringida.")
            ice_servers.append(
                RTCIceServer(
                    urls=turn_url,
                    username=turn_user,
                    credential=turn_pass,
                )
            )

        return RTCConfiguration(iceServers=ice_servers)

    def create_peer(self, on_data_message, on_datachannel_ready):
        pc = RTCPeerConnection(configuration=self._build_rtc_configuration())
        self.video_pipeline.attach_track_to_peer(pc)

        @pc.on("datachannel")
        def on_datachannel(canal):
            logger.info("Canal de datos establecido: %s", canal.label)
            on_datachannel_ready(canal)

            @canal.on("message")
            def on_message(mensaje):
                on_data_message(mensaje)

        return pc
