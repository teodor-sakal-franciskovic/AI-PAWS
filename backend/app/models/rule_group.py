from sqlalchemy import Column, Float, ForeignKey, Integer, String

from .base import AcademicWritingSchema


class RuleGroup(AcademicWritingSchema):
    __tablename__ = "rule_group"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    percentage_of_points_in_assignment = Column(
        "percentage_of_points_in_assignment", Float
    )
    created_by = Column("created_by", Integer, ForeignKey("user.id"))
    updated_by = Column("updated_by", Integer, ForeignKey("user.id"))
