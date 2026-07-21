from pydantic import BaseModel
from typing import Optional

from .rule import RuleCreate, RuleResponse, RuleUpdate


class RuleGroupCreate(BaseModel):
    name: str
    percentage_of_points_in_assignment: Optional[float] = None
    rules: list[RuleCreate]


class RuleGroupUpdate(BaseModel):
    id: Optional[int] = None
    name: str
    percentage_of_points_in_assignment: Optional[float] = None
    rules: list[RuleUpdate]


class RuleGroupResponse(BaseModel):
    id: int
    name: str
    percentage_of_points_in_assignment: Optional[float] = None
    rules: list[RuleResponse] = []

    class Config:
        from_attributes = True
