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


class GradingAssignmentResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    max_points: float | None = None


class GradingResultResponse(BaseModel):
    fulfillment_ratio: float
    achieved_points: float | None = None


class GradingSubmissionResponse(BaseModel):
    submission_id: int
    submission_status: str
    grading_status: str
    submitted_at: datetime
    assignment: GradingAssignmentResponse
    result: GradingResultResponse | None = None


class GradingSummaryResponse(BaseModel):
    completed_submissions_count: int
    ungraded_submissions_count: int
    achieved_points: float
    max_points: float


class StudentWithSubmissionsResponse(BaseModel):
    student_id: int
    student_index: str | None = None
    name: str
    surname: str
    summary: GradingSummaryResponse
    submissions: list[GradingSubmissionResponse] = []


class StudentsWithSubmissionsResponse(BaseModel):
    students_with_submissions: list[StudentWithSubmissionsResponse] = []
