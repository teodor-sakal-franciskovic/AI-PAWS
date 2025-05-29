from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text

from .base import AcademicWritingSchema


class Rule(AcademicWritingSchema):
    __tablename__ = "rule"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    description = Column("description", String)
    include_in_prompt = Column(
        "include_in_prompt", Boolean, server_default=text("true")
    )
    grading_aspect_id = Column(
        "grading_aspect_id", Integer, ForeignKey("grading_aspect.id")
    )
