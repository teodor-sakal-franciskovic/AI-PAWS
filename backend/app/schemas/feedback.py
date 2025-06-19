from pydantic import BaseModel


class InteractiveFeedbackResponse(BaseModel):
    id: int
    feedback_text: str
    initially_fulfilled: bool
    rule_name: str
    rule_description: str
    additional_text: str
