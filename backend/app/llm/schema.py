from typing import List, Optional

from pydantic import BaseModel, Field


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
    rule_id: int
    evidence: List[str]
    grade: int = Field(ge=0, le=2)
    grade_explanation: str


class LLMEvaluationResponse(BaseModel):
    evaluation: List[LLMRuleEvaluation]


class LLMCompiledRule(BaseModel):
    rule_id: int
    checks: List[str] = Field(min_length=1, max_length=4)
    grade_2: str
    grade_1: str
    grade_0: str
    generated_description: str


class LLMRuleGroupCompilation(BaseModel):
    rules: List[LLMCompiledRule]


class LLMInitialKnowledgeResponse(BaseModel):
    initial_student_knowledge: str
