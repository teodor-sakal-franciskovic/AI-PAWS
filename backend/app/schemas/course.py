from datetime import datetime

from pydantic import BaseModel

from .assignment import AssignmentCreate, AssignmentDetailResponse, AssignmentUpdate
from .audit import AuditResponse
from .group import StudentGroupResponse
from .language import LanguageResponse
from .user import UserSummaryResponse


class CourseCreate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: float | None = None
    feedback_language_id: int
    submission_language_ids: list[int]
    instructor_ids: list[int]
    assignments: list[AssignmentCreate]


class CourseUpdate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: float | None = None
    feedback_language_id: int
    submission_language_ids: list[int]
    instructor_ids: list[int]
    assignments: list[AssignmentUpdate]


class CourseDetailResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    max_amount_of_points: float | None = None
    feedback_language: LanguageResponse
    submission_languages: list[LanguageResponse] = []
    student_groups: list[StudentGroupResponse] = []
    instructors: list[UserSummaryResponse] = []
    assignments: list[AssignmentDetailResponse] = []
    audit: AuditResponse

    class Config:
        from_attributes = True
