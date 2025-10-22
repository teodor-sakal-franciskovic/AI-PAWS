from typing import List, Optional

from pydantic import BaseModel


class LLMRuleFeedback(BaseModel):
    rule_name: str
    correction: Optional[str] = None
    correction_explanation: Optional[str] = None
    validity_explanation: Optional[str] = None


class LLMFeedbackResponse(BaseModel):
    feedback: List[LLMRuleFeedback]
    updated_knowledge: str


class LLMAdditionalFeedbackResponse(BaseModel):
    additional_explanation: str
    updated_knowledge: str


class LLMRuleEvaluation(BaseModel):
    rule_name: str
    grade: int
    grade_explanation: str


class LLMEvaluationResponse(BaseModel):
    evaluation: List[LLMRuleEvaluation]


class LLMUpdatedKnowledge(BaseModel):
    updated_knowledge: str


class LLMInitialKnowledgeResponse(BaseModel):
    initial_student_knowledge: str
