import base64
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from .rule import EvaluativeRuleSchema


class RuleFeedbackSchema(BaseModel):
    feedback_id: int
    is_valid: bool
    rule_name: str
    rule_description: str
    feedback_text: Any
    additional_feedback_text: str
    fulfillment_value: Any
    initially_fulfilled: bool


class SubmissionResponse(BaseModel):
    id: int
    submitted_at: datetime
    text: str | None
    achieved_points_percentage: Any
    submission_mode: str
    status: Any
    rule_feedbacks: list[RuleFeedbackSchema]
    file_bytes: bytes | None = None

    model_config = ConfigDict(
        json_encoders={bytes: lambda v: base64.b64encode(v).decode("utf-8")}
    )


class EvaluativeSubmissionSchema(BaseModel):
    submission_id: int
    status: str
    submitted_at: datetime
    assignment_name: str
    assignment_start_date: datetime
    assignment_end_date: datetime
    achieved_points_percentage: Any
    rules: list[EvaluativeRuleSchema]


class TAEvaluationGrade(BaseModel):
    feedback_id: int
    final_grade: int
    fulfillment_id: int
    final_feedback: str


class TAEvaluationGradesRequest(BaseModel):
    evaluation_grades: list[TAEvaluationGrade]
