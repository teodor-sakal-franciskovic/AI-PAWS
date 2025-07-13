from pydantic import BaseModel
from typing import Any


class EvaluativeFulfillmentSchema(BaseModel):
    fulfillment_id: int
    initial_fulfillment_value: Any
    final_fulfillment_value: Any
