from pydantic import BaseModel
from typing import Any


class InteractiveFeedbackResponse(BaseModel):
    id: int
    feedback_text: str
    initially_fulfilled: bool
    rule_name: str
    rule_description: str
    additional_text: str


class EvaluativeFeedbackResponse(BaseModel):
    id: int
    rule_name: str
    rule_description: str
    grade: Any
    grade_explanation: str
