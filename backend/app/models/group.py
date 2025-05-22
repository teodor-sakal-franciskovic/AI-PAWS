from sqlalchemy import (TIMESTAMP, Boolean, Column, ForeignKey, Integer,
                        String, func)

from .base import AcademicWritingSchema


class Group(AcademicWritingSchema):
    __tablename__ = "group"

    id = Column("id", Integer, primary_key=True)
    valid_from = Column("valid_from", TIMESTAMP, nullable=False)
    valid_until = Column("valid_until", TIMESTAMP, nullable=False)