from pydantic import BaseModel, Field


class MotorCapability(BaseModel):
    nombre: str
    canal: int
    direccion_i2c: int = 0x40


class ServoCapability(BaseModel):
    nombre: str
    canal: int
    angulo_min: int
    angulo_max: int
    direccion_i2c: int = 0x40


class ActuatorCapability(BaseModel):
    nombre: str
    canales: dict[str, int]
    limites: dict[str, tuple[int, int]]
    pin_accion: int | None = None
    direccion_i2c: int = 0x40


class CameraCapability(BaseModel):
    nombre: str
    fps: int
    resolucion: tuple[int, int]
    tipo: str = "configurada"


class DeviceCapabilities(BaseModel):
    schema_version: str = Field(default="1.0.0")
    device_id: str
    device_fingerprint: str
    motores: list[MotorCapability]
    servos_direccion: list[ServoCapability]
    actuadores_multieje: list[ActuatorCapability]
    camaras: list[CameraCapability]
