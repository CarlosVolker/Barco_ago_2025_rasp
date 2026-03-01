import asyncio
import logging
import signal

from cliente_vehiculo import ClienteVehiculo
from controladores.instancias import motores
from src.edge_agent.bootstrap.logging import configure_logging
from src.edge_agent.bootstrap.settings import get_settings
from src.edge_agent.identity.device_id import get_device_id

logger = logging.getLogger("edge_agent.app")


async def shutdown(loop, received_signal=None):
    if received_signal:
        logger.info("Recibida senal de salida %s...", received_signal.name)

    logger.info("Deteniendo motores por seguridad...")
    for motor in motores:
        try:
            motor.establecer_velocidad(0)
        except Exception:
            pass

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    logger.info("Cancelando %d tareas pendientes", len(tasks))
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


def main():
    settings = get_settings()
    configure_logging(settings.log_level, device_id=get_device_id())

    logger.info("Iniciando Sistema de Control de Vehiculo IoT...")
    cliente = ClienteVehiculo()
    loop = asyncio.get_event_loop()

    signal_names = ("SIGHUP", "SIGTERM", "SIGINT")
    for name in signal_names:
        sig = getattr(signal, name, None)
        if sig is not None:
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(loop, received_signal=s)))

    try:
        loop.run_until_complete(cliente.iniciar())
    except Exception as exc:
        logger.error("Error fatal en la ejecucion: %s", exc)
    finally:
        logger.info("Sistema apagado.")
