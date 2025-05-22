from sqlalchemy import Column, Integer, String

from .base import AcademicWritingSchema


class SubmissionMode(AcademicWritingSchema):
    __tablename__ = "submission_mode"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    description = Column("description", String, nullable=False)
