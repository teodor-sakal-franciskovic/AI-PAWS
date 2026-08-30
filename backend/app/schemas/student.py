from pydantic import BaseModel, field_validator

from .group import GroupStudentResponse


class StudentSearchResponse(BaseModel):
    items: list[GroupStudentResponse]
    total: int
    page: int
    page_size: int


class StudentBatchItem(BaseModel):
    name: str
    surname: str
    email: str
    faculty: str
    index: str

    @field_validator("name", "surname", mode="after")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()

    @field_validator("email", mode="after")
    @classmethod
    def _normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("index", mode="after")
    @classmethod
    def _strip_index(cls, v: str) -> str:
        return v.strip()


class StudentBatchRegisterRequest(BaseModel):
    students: list[StudentBatchItem]


class StudentBatchRegisterResponse(BaseModel):
    registered_count: int


class StudentBatchErrorItem(BaseModel):
    row_number: int
    field: str | None
    code: str
    message: str
