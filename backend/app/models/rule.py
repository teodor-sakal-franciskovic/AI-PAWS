from sqlalchemy import Column, ForeignKey, Integer, String

from .base import AcademicWritingSchema


class Rule(AcademicWritingSchema):
    __tablename__ = "rule"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    description = Column("description", String)
    grading_aspect_id = Column("grading_aspect_id", Integer, ForeignKey("grading_aspect.id"))
