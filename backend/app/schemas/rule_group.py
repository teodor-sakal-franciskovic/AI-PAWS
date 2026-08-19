from pydantic import BaseModel
from typing import Optional

from .rule import RuleCreate, RuleResponse, RuleUpdate
from .user import UserSummaryResponse


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


class RuleGroupListItemResponse(BaseModel):
    id: int
    name: str
    percentage_of_points_in_assignment: Optional[float] = None
    number_of_courses: int
    rules: list[RuleResponse] = []
    created_by: Optional[UserSummaryResponse] = None
    updated_by: Optional[UserSummaryResponse] = None

    class Config:
        from_attributes = True


class RuleGroupDetailResponse(RuleGroupListItemResponse):
    taken_rule_group_names: list[str] = []


class RuleGroupNameCheckResponse(BaseModel):
    rule_name_used: bool
