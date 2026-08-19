from pydantic import BaseModel
from typing import Optional

from .feedback import EvaluativeFeedbackSchema
from .fulfillment import EvaluativeFulfillmentSchema


class EvaluativeRuleSchema(BaseModel):
    rule_id: int
    name: str
    description: str
    feedback: EvaluativeFeedbackSchema
    fulfillment: EvaluativeFulfillmentSchema


class RuleCreate(BaseModel):
    name: str
    user_description: str
    include_in_prompt: bool = True


class RuleUpdate(BaseModel):
    id: Optional[int] = None
    name: str
    user_description: str
    include_in_prompt: bool = True


class RuleResponse(BaseModel):
    id: int
    name: str
    user_description: str
    include_in_prompt: bool

    class Config:
        from_attributes = True
