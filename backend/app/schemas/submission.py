from pydantic import BaseModel
from typing import Any, List
from datetime import datetime

from .rule import EvaluativeRuleSchema


class SubmissionResponse(BaseModel):
    id: int
    submitted_at: datetime
    text: str
    gd_file_id: str
    gd_file_link: str
    achieved_points_percentage: Any
    submission_mode: str


class EvaluativeSubmissionSchema(BaseModel):
    submission_id: int
    submitted_at: datetime
    gd_file_link: str
    achieved_points_percentage: Any
    rules: List[EvaluativeRuleSchema]


class TAEvaluationGrade(BaseModel):
    feedback_id: int
    final_grade: int
    fulfillment_id: int
    final_feedback: str


class TAEvaluationGradesRequest(BaseModel):
    evaluation_grades: List[TAEvaluationGrade]
