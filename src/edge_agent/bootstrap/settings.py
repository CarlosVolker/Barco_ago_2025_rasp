from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EdgeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    url_backend: str = Field(default="https://tu-api-backend.com", validation_alias="URL_BACKEND")
    url_signaling: str = Field(default="wss://tu-api-backend.com/ws/vehiculo/", validation_alias="URL_SIGNALING")

    servidor_stun: str = Field(default="stun:stun.l.google.com:19302", validation_alias="SERVIDOR_STUN")
    servidor_turn_url: str | None = Field(default=None, validation_alias="SERVIDOR_TURN_URL")
    servidor_turn_user: str | None = Field(default=None, validation_alias="SERVIDOR_TURN_USER")
    servidor_turn_pass: str | None = Field(default=None, validation_alias="SERVIDOR_TURN_PASS")

    telemetry_interval_s: int = Field(default=10, validation_alias="TELEMETRY_INTERVAL_S")
    telemetry_request_timeout_s: int = Field(default=10, validation_alias="TELEMETRY_REQUEST_TIMEOUT_S")
    control_deadman_ms: int = Field(default=300, validation_alias="CONTROL_DEADMAN_MS")
    observability_log_interval_s: int = Field(default=30, validation_alias="OBSERVABILITY_LOG_INTERVAL_S")
    video_profile: Literal["low", "balanced", "high"] = Field(default="balanced", validation_alias="VIDEO_PROFILE")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")


def get_settings() -> EdgeSettings:
    return EdgeSettings()
