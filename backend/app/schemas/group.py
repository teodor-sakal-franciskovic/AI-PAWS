from datetime import datetime

from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    short_name: str | None = None
    valid_from: datetime
    valid_until: datetime
    course_id: int
    student_ids: list[int] = []

    def __str__(self):
        return (
            f"GroupCreate(name='{self.name}', "
            f"valid_from='{self.valid_from.strftime('%Y-%m-%d %H:%M:%S')}', "
            f"valid_until='{self.valid_until.strftime('%Y-%m-%d %H:%M:%S')}')"
        )


class GroupUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    student_ids: list[int] | None = None


class StudentIdsRequest(BaseModel):
    student_ids: list[int]


class GroupResponse(BaseModel):
    id: int
    name: str
    short_name: str | None = None
    valid_from: datetime
    valid_until: datetime

    class Config:
        from_attributes = True


class StudentGroupResponse(BaseModel):
    """Lightweight group representation used for lookups and nested display."""

    id: int
    name: str
    short_name: str | None = None

    class Config:
        from_attributes = True


class CourseGroupsResponse(BaseModel):
    course_id: int
    course_name: str
    groups: list[GroupResponse] = []


class GroupStudentResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: str
    index: str | None = None
    faculty: str | None = None
    is_active: bool

    class Config:
        from_attributes = True
