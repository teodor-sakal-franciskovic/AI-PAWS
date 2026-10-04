from typing import Any

from pydantic import BaseModel


# TODO - Mozda menjati response za additional
class InteractiveFeedbackResponse(BaseModel):
    id: int
    feedback_text: str
    initially_fulfilled: bool
    rule_name: str
    rule_description: str
    additional_feedback_text: str
    is_valid: bool


class EvaluativeFeedbackSchema(BaseModel):
    feedback_id: int
    feedback_text: Any
    final_feedback_text: Any
