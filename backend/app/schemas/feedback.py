from pydantic import BaseModel
from typing import Any


# TODO - Mozda menjati response za additional
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


class EvaluativeFeedbackSchema(BaseModel):
    feedback_id: int
    feedback_text: Any
    final_feedback_text: Any
