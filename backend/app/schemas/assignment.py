from pydantic import BaseModel
from datetime import datetime
from typing import Any


class AssignmentCreate(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime
    submission_mode_id: int
    chapter_id: int
    group_ids: list[int]


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
    submission: Any
