from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

from .rule_group import RuleGroupCreate


class AssignmentCreate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    chapter_id: int
    submission_mode_id: int
    percentage_of_points_in_course: Optional[float] = None
    rule_groups: list[RuleGroupCreate]


class AssignmentResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    submission_mode_id: int
    submission_mode_name: str
    chapter_id: int
    chapter_name: str


class SubmittedSubmissionForAssignmentResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    submission_mode: str
    chapter_id: int
    chapter_name: str
    submission: Any
