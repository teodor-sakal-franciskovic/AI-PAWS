from typing import List, Optional

from pydantic import BaseModel


class LLMRuleFeedback(BaseModel):
    rule_name: str
    correction: Optional[str] = None
    correction_explanation: Optional[str] = None
    validity_explanation: Optional[str] = None


class LLMFeedbackResponse(BaseModel):
    feedback: List[LLMRuleFeedback]
