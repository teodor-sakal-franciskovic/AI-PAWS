from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from .assignment import AssignmentCreate


class CourseCreate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: Optional[float] = None
    feedback_language_id: int
    submission_language_ids: list[int]
    group_ids: list[int]
    assignments: list[AssignmentCreate]


class CourseResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: Optional[float]
    feedback_language_id: int

    class Config:
        from_attributes = True
