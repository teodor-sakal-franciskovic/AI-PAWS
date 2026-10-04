from datetime import datetime

from pydantic import BaseModel, Field


class RuleEvaluationRequest(BaseModel):
    rule_id: int
    final_feedback_text: str
    final_fulfillment_value: int = Field(ge=0, le=2)


class FinalEvaluationRequest(BaseModel):
    rule_evaluations: list[RuleEvaluationRequest]


class EvaluationCourseResponse(BaseModel):
    id: int
    name: str


class EvaluationStudentResponse(BaseModel):
    student_id: int
    student_index: str | None = None
    name: str
    surname: str


class EvaluationAssignmentResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    max_points: float | None = None


class SubmissionFileResponse(BaseModel):
    name: str
    mime_type: str
    download_url: str


class EvaluationSubmissionResponse(BaseModel):
    id: int
    status: str
    submitted_at: datetime
    file: SubmissionFileResponse | None = None


class EvaluationResultResponse(BaseModel):
    fulfillment_ratio: float
    achieved_points: float | None = None


class GradedByResponse(BaseModel):
    instructor_id: int
    name: str
    surname: str


class EvaluationResponse(BaseModel):
    grading_status: str
    ai_suggested_result: EvaluationResultResponse | None = None
    final_result: EvaluationResultResponse | None = None
    graded_at: datetime | None = None
    graded_by: GradedByResponse | None = None


class FulfillmentScaleItemResponse(BaseModel):
    value: int
    code: str


class RuleFeedbackValueResponse(BaseModel):
    feedback_text: str | None = None
    fulfillment_value: int | None = None


class RuleEvaluationDetailResponse(BaseModel):
    ai_suggestion: RuleFeedbackValueResponse
    final: RuleFeedbackValueResponse | None = None


class EvaluationRuleResponse(BaseModel):
    id: int
    position: int
    name: str
    description: str | None = None
    evaluation: RuleEvaluationDetailResponse


class RuleGroupEvaluationSummaryResponse(BaseModel):
    rules_count: int
    finalized_rules_count: int
    max_points: float | None = None
    ai_suggested_achieved_points: float | None = None
    final_achieved_points: float | None = None


class EvaluationRuleGroupResponse(BaseModel):
    id: int | None = None
    name: str | None = None
    position: int
    percentage_of_points_in_assignment: float | None = None
    summary: RuleGroupEvaluationSummaryResponse
    rules: list[EvaluationRuleResponse] = []


class EvaluationPermissionsResponse(BaseModel):
    can_view: bool
    can_grade: bool
    can_edit_grade: bool


class SubmissionEvaluationResponse(BaseModel):
    course: EvaluationCourseResponse
    student: EvaluationStudentResponse
    assignment: EvaluationAssignmentResponse
    submission: EvaluationSubmissionResponse
    evaluation: EvaluationResponse
    fulfillment_scale: list[FulfillmentScaleItemResponse]
    rule_groups: list[EvaluationRuleGroupResponse] = []
    permissions: EvaluationPermissionsResponse
