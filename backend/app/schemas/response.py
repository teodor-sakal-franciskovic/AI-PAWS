from pydantic import BaseModel
from typing import Any


class GenericResponse(BaseModel):
    message: str
    data: Any


class NameAvailabilityResponse(BaseModel):
    name_available: bool


class IdResponse(BaseModel):
    id: int
