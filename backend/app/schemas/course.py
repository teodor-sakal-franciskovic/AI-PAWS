from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from .assignment import AssignmentCreate, AssignmentDetailResponse, AssignmentUpdate


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


class CourseUpdate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: Optional[float] = None
    feedback_language_id: int
    submission_language_ids: list[int]
    group_ids: list[int]
    instructor_ids: list[int]
    assignments: list[AssignmentUpdate]


class LanguageResponse(BaseModel):
    id: int
    name: str
    short_name: str

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserSummaryResponse(BaseModel):
    id: int
    name: str
    surname: str

    class Config:
        from_attributes = True


class CourseDetailResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: Optional[float] = None
    feedback_language: LanguageResponse
    submission_languages: list[LanguageResponse] = []
    groups: list[GroupResponse] = []
    created_by: Optional[UserSummaryResponse] = None
    updated_by: Optional[UserSummaryResponse] = None
    instructors: list[UserSummaryResponse] = []
    assignments: list[AssignmentDetailResponse] = []

    class Config:
        from_attributes = True
