from datetime import datetime
from typing import Any

from pydantic import BaseModel

from .rule_group import RuleGroupLink, RuleGroupResponse


class AssignmentCreate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    submission_mode_id: int
    percentage_of_points_in_course: float | None = None
    rule_groups: list[RuleGroupLink]


class AssignmentResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    submission_mode_id: int
    submission_mode_name: str
    chapter_id: int
    chapter_name: str


class AssignmentUpdate(BaseModel):
    id: int | None = None
    name: str
    start_date: datetime
    end_date: datetime
    submission_mode_id: int
    percentage_of_points_in_course: float | None = None
    rule_groups: list[RuleGroupLink]


class AssignmentDetailResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    submission_mode_id: int
    submission_mode_name: str
    percentage_of_points_in_course: float | None = None
    rule_groups: list[RuleGroupResponse] = []

    class Config:
        from_attributes = True


class SubmittedSubmissionForAssignmentResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    submission_mode: str
    chapter_id: int
    chapter_name: str
    submission: Any
