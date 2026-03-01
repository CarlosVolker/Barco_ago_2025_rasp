from typing import Any

from pydantic import BaseModel


class SignalEnvelope(BaseModel):
    target: str | None = None
    type: str
    payload: Any
