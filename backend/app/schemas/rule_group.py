from pydantic import BaseModel
from typing import Optional

from .audit import AuditResponse
from .rule import RuleCreate, RuleResponse, RuleUpdate


class RuleGroupCreate(BaseModel):
    name: str
    rules: list[RuleCreate]


class RuleGroupUpdate(BaseModel):
    name: str
    rules: list[RuleUpdate]


class RuleGroupLink(BaseModel):
    """A reference to an existing rule group from within an assignment payload."""

    id: int
    percentage_of_points_in_assignment: Optional[float] = None


class RuleGroupResponse(BaseModel):
    """The rule group as it's nested inside a course/assignment response."""

    id: int
    name: str
    percentage_of_points_in_assignment: Optional[float] = None
    rules: list[RuleResponse] = []

    class Config:
        from_attributes = True


class RuleGroupDetailResponse(BaseModel):
    """The rule group as returned by the standalone /rule-groups endpoints."""

    id: int
    name: str
    number_of_courses: int
    rules: list[RuleResponse] = []
    audit: AuditResponse

    class Config:
        from_attributes = True
