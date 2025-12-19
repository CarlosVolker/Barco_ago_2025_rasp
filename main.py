
import asyncio
import logging
import signal
from cliente_vehiculo import ClienteVehiculo
from controladores.instancias import motores

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VehiculoMain")

async def shutdown(loop, signal=None):
    """Limpia los recursos antes de salir."""
    if signal:
        logger.info(f"Recibida señal de salida {signal.name}...")
    
    logger.info("Deteniendo motores por seguridad...")
    for motor in motores:
        try:
            motor.establecer_velocidad(0)
        except:
            pass
    
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    
    logger.info(f"Cancelando {len(tasks)} tareas pendientes")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

def main():
    """
    Punto de entrada principal para el controlador genérico de vehículos en Raspberry Pi 4.
    """
    logger.info("Iniciando Sistema de Control de Vehículo IoT...")
    
    cliente = ClienteVehiculo()
    loop = asyncio.get_event_loop()

    # Manejo de señales para un cierre seguro
    for s in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(loop, signal=s))
        )

    try:
        loop.run_until_complete(cliente.iniciar())
    except Exception as e:
        logger.error(f"Error fatal en la ejecución: {e}")
    finally:
        logger.info("Sistema apagado.")

if __name__ == "__main__":
    main()
