from pydantic import BaseModel, ConfigDict, Field


class TelemetryPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    num_serie: str
    estado: str = "online"
    bateria: float
    latitud: float
    longitud: float
    intensidad_senal: int = Field(alias="intensidad_señal")
    temperatura_cpu: float
    latencia: int = Field(ge=0)
