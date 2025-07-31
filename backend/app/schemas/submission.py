from pydantic import BaseModel
from typing import Any, List
from datetime import datetime

from .rule import EvaluativeRuleSchema


class RuleFeedbackSchema(BaseModel):
    feedback_id: int
    rule_name: str
    rule_description: str
    feedback_text: Any
    additional_feedback_text: str
    fulfillment_value: Any


class SubmissionResponse(BaseModel):
    id: int
    submitted_at: datetime
    text: str
    achieved_points_percentage: Any
    submission_mode: str
    rule_feedbacks: list[RuleFeedbackSchema]


class EvaluativeSubmissionSchema(BaseModel):
    submission_id: int
    submitted_at: datetime
    gd_file_link: str
    assignment_name: str
    assignment_start_date: datetime
    assignment_end_date: datetime
    achieved_points_percentage: Any
    rules: List[EvaluativeRuleSchema]


class TAEvaluationGrade(BaseModel):
    feedback_id: int
    final_grade: int
    fulfillment_id: int
    final_feedback: str


class TAEvaluationGradesRequest(BaseModel):
    evaluation_grades: List[TAEvaluationGrade]
