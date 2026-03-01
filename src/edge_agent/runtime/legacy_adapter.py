import json
import logging
from typing import Any

from pydantic import TypeAdapter, ValidationError

from src.edge_agent.capabilities.builder import build_capabilities
from src.edge_agent.contracts.control import ControlCommand
from src.edge_agent.contracts.telemetry import TelemetryPayload

logger = logging.getLogger("edge_agent.runtime.legacy_adapter")
_CONTROL_ADAPTER = TypeAdapter(ControlCommand)


def build_inicio_payload(num_serie: str) -> dict[str, Any]:
    caps = build_capabilities()
    return {
        "num_serie": num_serie,
        "config": caps.model_dump(mode="json"),
    }


def validate_control_command(raw_command: str | dict[str, Any]):
    try:
        data = json.loads(raw_command) if isinstance(raw_command, str) else raw_command
        return _CONTROL_ADAPTER.validate_python(data)
    except (ValidationError, json.JSONDecodeError) as exc:
        logger.warning("Invalid control command rejected: %s", exc)
        return None


def build_telemetry_payload(**kwargs) -> dict[str, Any]:
    payload = TelemetryPayload(**kwargs)
    return payload.model_dump(by_alias=True)
