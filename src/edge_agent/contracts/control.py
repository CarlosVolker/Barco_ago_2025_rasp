from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class MovementCommand(BaseModel):
    tipo: Literal["movimiento"]
    velocidad: int = Field(default=0, ge=-100, le=100)
    giro: int = Field(default=90, ge=0, le=180)


class MotorIndividualCommand(BaseModel):
    tipo: Literal["motor_individual"]
    indice: int = Field(default=0, ge=0)
    velocidad: int = Field(default=0, ge=-100, le=100)


class ActuatorCommand(BaseModel):
    tipo: Literal["actuador_multieje"]
    indice: int = Field(default=0, ge=0)
    eje: str | None = None
    angulo: int | None = Field(default=None, ge=0, le=180)
    ejecutar_accion: bool = False


class StopCommand(BaseModel):
    tipo: Literal["parar"]


ControlCommand = Annotated[
    Union[MovementCommand, MotorIndividualCommand, ActuatorCommand, StopCommand],
    Field(discriminator="tipo"),
]
