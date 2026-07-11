from typing import Any, Dict

from pydantic import BaseModel


class HealthResponseDto(BaseModel):
    status: str
    info: Dict[str, Any] = {}
    error: Dict[str, Any] = {}
    details: Dict[str, Any] = {}
