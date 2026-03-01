import hashlib
import logging
import os
import platform

logger = logging.getLogger("edge_agent.identity.device_id")


def _read_cpu_serial() -> str:
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Serial"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass

    fallback = f"{platform.node()}-{os.getenv('HOSTNAME', 'unknown-host')}"
    logger.warning("CPU serial unavailable, using fallback host fingerprint")
    return fallback


def get_device_fingerprint() -> str:
    serial = _read_cpu_serial()
    digest = hashlib.sha256(serial.encode("utf-8")).hexdigest()[:16]
    return f"rpi-{digest}"


def get_device_id() -> str:
    serial = _read_cpu_serial()
    digest = hashlib.sha256(serial.encode("utf-8")).hexdigest()[:8]
    return f"rpi-{digest}"
