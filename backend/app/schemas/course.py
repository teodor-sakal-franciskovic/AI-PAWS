from datetime import datetime

from pydantic import BaseModel

from .assignment import AssignmentCreate, AssignmentDetailResponse, AssignmentUpdate
from .language import LanguageResponse
from .user import UserSummaryResponse


class CourseCreate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: float | None = None
    feedback_language_id: int
    submission_language_ids: list[int]
    group_ids: list[int]
    assignments: list[AssignmentCreate]


class CourseResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: float | None
    feedback_language_id: int

    class Config:
        from_attributes = True


class CourseUpdate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: float | None = None
    feedback_language_id: int
    submission_language_ids: list[int]
    group_ids: list[int]
    instructor_ids: list[int]
    assignments: list[AssignmentUpdate]


class GroupResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CourseDetailResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: float | None = None
    feedback_language: LanguageResponse
    submission_languages: list[LanguageResponse] = []
    groups: list[GroupResponse] = []
    created_by: UserSummaryResponse | None = None
    updated_by: UserSummaryResponse | None = None
    instructors: list[UserSummaryResponse] = []
    assignments: list[AssignmentDetailResponse] = []

    class Config:
        from_attributes = True


class CourseWithTakenNamesResponse(CourseDetailResponse):
    taken_course_names: list[str] = []


class CourseNameCheckResponse(BaseModel):
    course_name_used: bool
