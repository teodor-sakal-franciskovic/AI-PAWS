from sqlalchemy import TIMESTAMP, Column, Integer, String

from .base import AcademicWritingSchema


class Group(AcademicWritingSchema):
    __tablename__ = "group"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    valid_from = Column("valid_from", TIMESTAMP, nullable=False)
    valid_until = Column("valid_until", TIMESTAMP, nullable=False)