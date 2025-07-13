from pydantic import BaseModel

from .feedback import EvaluativeFeedbackSchema
from .fulfillment import EvaluativeFulfillmentSchema


class EvaluativeRuleSchema(BaseModel):
    rule_id: int
    name: str
    description: str
    feedback: EvaluativeFeedbackSchema
    fulfillment: EvaluativeFulfillmentSchema
