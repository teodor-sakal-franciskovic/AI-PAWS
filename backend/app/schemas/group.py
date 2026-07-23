from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str
    valid_from: datetime
    valid_until: datetime

    def __str__(self):
        return (
            f"GroupCreate(name='{self.name}', "
            f"valid_from='{self.valid_from.strftime('%Y-%m-%d %H:%M:%S')}', "
            f"valid_until='{self.valid_until.strftime('%Y-%m-%d %H:%M:%S')}')"
        )


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class GroupResponse(BaseModel):
    id: int
    name: str
    valid_from: datetime
    valid_until: datetime

    class Config:
        from_attributes = True


class CourseGroupsResponse(BaseModel):
    course_id: int
    course_name: str
    groups: List[GroupResponse] = []


class GroupStudentResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: str
    index: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
