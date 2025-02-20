from pydantic import BaseModel
from typing import Any


class GenericResponse(BaseModel):
    message: str
    data: Any
