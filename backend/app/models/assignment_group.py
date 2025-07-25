from sqlalchemy import Column, Integer, ForeignKey

from .base import AcademicWritingSchema


class AssignmentGroup(AcademicWritingSchema):
    __tablename__ = "assignment_group"

    assignment_id = Column(
        "assignment_id", Integer, ForeignKey("assignment.id"), primary_key=True
    )
    group_id = Column("group_id", Integer, ForeignKey("group.id"), primary_key=True)
