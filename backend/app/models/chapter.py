from sqlalchemy import Column, Integer, String

from .base import AcademicWritingSchema


class Chapter(AcademicWritingSchema):
    __tablename__ = "chapter"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String, nullable=False)
