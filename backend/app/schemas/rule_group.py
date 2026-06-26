from pydantic import BaseModel
from typing import Optional

from .rule import RuleCreate


class RuleGroupCreate(BaseModel):
    name: str
    percentage_of_points_in_assignment: Optional[float] = None
    rules: list[RuleCreate]
