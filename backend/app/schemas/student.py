from pydantic import BaseModel

from .group import GroupStudentResponse


class StudentSearchResponse(BaseModel):
    items: list[GroupStudentResponse]
    total: int
    page: int
    page_size: int
