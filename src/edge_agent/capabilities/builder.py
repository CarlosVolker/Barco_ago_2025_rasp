import os
import shutil

from config.componentes import ACTUADORES_MULTIEJE, CAMARAS, MOTORES_PROPULSION, SERVOS_DIRECCION
from src.edge_agent.contracts.capabilities import CameraCapability, DeviceCapabilities
from src.edge_agent.identity.device_id import get_device_fingerprint, get_device_id


def _detect_camera_type() -> str:
    if shutil.which("rpicam-vid"):
        return "libcamera-csi"
    if os.path.exists("/dev/video0"):
        return "usb-v4l2"
    return "desconocida"


def build_capabilities() -> DeviceCapabilities:
    camera_type = _detect_camera_type()
    cameras = []

    for cam in CAMARAS:
        cameras.append(
            CameraCapability(
                nombre=cam.get("nombre", "camara"),
                fps=cam.get("fps", 15),
                resolucion=tuple(cam.get("resolucion", (640, 480))),
                tipo=camera_type,
            )
        )

    return DeviceCapabilities(
        device_id=get_device_id(),
        device_fingerprint=get_device_fingerprint(),
        motores=MOTORES_PROPULSION,
        servos_direccion=SERVOS_DIRECCION,
        actuadores_multieje=ACTUADORES_MULTIEJE,
        camaras=cameras,
    )
