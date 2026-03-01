import logging

from controladores.instancias import actuadores_multieje, motores, servos_direccion
from src.edge_agent.contracts.control import ActuatorCommand, MotorIndividualCommand, MovementCommand, StopCommand
from src.edge_agent.runtime.legacy_adapter import validate_control_command

logger = logging.getLogger("edge_agent.control.runtime")


class ControlRuntime:
    def __init__(self):
        self.motores = motores
        self.servos_direccion = servos_direccion
        self.actuadores_multieje = actuadores_multieje

    def process_command(self, raw_command) -> bool:
        try:
            comando = validate_control_command(raw_command)
            if comando is None:
                return False

            if isinstance(comando, MovementCommand):
                for motor in self.motores:
                    motor.establecer_velocidad(comando.velocidad)
                for servo in self.servos_direccion:
                    servo.establecer_angulo(comando.giro)
                return True

            if isinstance(comando, MotorIndividualCommand):
                idx = comando.indice
                if idx < len(self.motores):
                    self.motores[idx].establecer_velocidad(comando.velocidad)
                    return True

                logger.warning("Indice de motor %s fuera de rango.", idx)
                return False

            if isinstance(comando, ActuatorCommand):
                idx = comando.indice
                if idx >= len(self.actuadores_multieje):
                    logger.warning("Indice de actuador %s fuera de rango.", idx)
                    return False

                actuador = self.actuadores_multieje[idx]
                if comando.eje is not None and comando.angulo is not None:
                    actuador.mover_eje(comando.eje, comando.angulo)
                if comando.ejecutar_accion:
                    actuador.ejecutar_accion()
                return True

            if isinstance(comando, StopCommand):
                self.stop_all_motors()
                logger.info("PARADA DE EMERGENCIA")
                return True

            logger.warning("Tipo de comando no soportado: %s", type(comando).__name__)
            return False
        except Exception as exc:
            logger.error("Error procesando comando de control: %s", exc)
            return False

    def stop_all_motors(self) -> None:
        for motor in self.motores:
            try:
                motor.establecer_velocidad(0)
            except Exception as exc:
                logger.warning("No se pudo detener motor %s: %s", getattr(motor, "nombre", "desconocido"), exc)
