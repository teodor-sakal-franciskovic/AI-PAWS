from sqlalchemy import Column, Float, ForeignKey, Integer

from .base import AcademicWritingSchema


class AssignmentRuleGroup(AcademicWritingSchema):
    __tablename__ = "assignment_rule_group"

    assignment_id = Column(
        "assignment_id", Integer, ForeignKey("assignment.id"), primary_key=True
    )
    rule_group_id = Column(
        "rule_group_id", Integer, ForeignKey("rule_group.id"), primary_key=True
    )
    percentage_of_points_in_assignment = Column(
        "percentage_of_points_in_assignment", Float
    )
