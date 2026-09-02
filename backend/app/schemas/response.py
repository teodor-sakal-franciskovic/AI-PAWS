from typing import Any

from pydantic import BaseModel


class GenericResponse(BaseModel):
    message: str
    data: Any


class NameAvailabilityResponse(BaseModel):
    name_available: bool


class IdResponse(BaseModel):
    id: int
