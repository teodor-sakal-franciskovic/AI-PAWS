from sqlalchemy import Column, Integer, String

from .base import AcademicWritingSchema


class GradingAspect(AcademicWritingSchema):
    __tablename__ = "grading_aspect"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    max_amount_of_points = Column("max_amount_of_points", Integer)