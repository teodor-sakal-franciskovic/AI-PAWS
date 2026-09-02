from typing import Any

from pydantic import BaseModel


class EvaluativeFulfillmentSchema(BaseModel):
    fulfillment_id: int
    initial_fulfillment_value: Any
    final_fulfillment_value: Any
