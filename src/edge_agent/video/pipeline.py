import logging
import platform
import subprocess

from aiortc.contrib.media import MediaPlayer

logger = logging.getLogger("edge_agent.video.pipeline")


class VideoPipeline:
    def __init__(self):
        self.player = None
        self.cam_process = None

    def start_linux_pipe(self):
        cmd = [
            "rpicam-vid",
            "-t",
            "0",
            "--inline",
            "--width",
            "1280",
            "--height",
            "720",
            "--framerate",
            "30",
            "--bitrate",
            "2500000",
            "--profile",
            "high",
            "--codec",
            "libav",
            "--libav-format",
            "mpegts",
            "--low-latency",
            "1",
            "--g",
            "10",
            "--flush",
            "-o",
            "-",
        ]

        opciones_ffmpeg = {
            "probesize": "32",
            "analyze_duration": "0",
            "fflags": "nobuffer",
            "flags": "low_delay",
            "reorder_queue_size": "0",
            "max_delay": "0",
        }

        self.cam_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.player = MediaPlayer(self.cam_process.stdout, format="mpegts", options=opciones_ffmpeg)
        return self.player

    def attach_track_to_peer(self, pc):
        try:
            if platform.system() == "Linux":
                if self.player is None:
                    logger.info("Iniciando camara con estrategia rpicam-vid (2.5Mbps + low latency).")
                    self.start_linux_pipe()
            else:
                if self.player is None:
                    self.player = MediaPlayer("video=Integrated Camera", format="dshow", options={})

            if self.player and self.player.video:
                pc.addTrack(self.player.video)
                logger.info("Pista de video anadida al peer WebRTC.")
        except Exception as exc:
            logger.error("Error al iniciar o adjuntar video: %s", exc)
            logger.info("Continuando sin video...")

    def stop(self):
        player = self.player
        self.player = None

        if player:
            try:
                if getattr(player, "audio", None):
                    player.audio.stop()
                if getattr(player, "video", None):
                    player.video.stop()
            except Exception as exc:
                logger.debug("Error cerrando MediaPlayer: %s", exc)

        if self.cam_process:
            logger.info("Terminando proceso de camara...")
            self.cam_process.terminate()
            try:
                self.cam_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                logger.warning("La camara no se cerro a tiempo, forzando kill...")
                self.cam_process.kill()
            finally:
                self.cam_process = None
